# client/client_etudiant.py
import socket
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HOST = "127.0.0.1"
PORT = 5000

def envoyer(action, params={}):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        requete = json.dumps({"action": action, "params": params})
        s.send(requete.encode('utf-8'))
        reponse = s.recv(4096).decode('utf-8')
        return json.loads(reponse)

def afficher_menu():
    print("\n" + "="*45)
    print("   INTERFACE ÉTUDIANT — Consultation Notes")
    print("="*45)
    print("  1. Voir mes notes")
    print("  2. Voir ma moyenne")
    print("  3. Voir mon bulletin complet")
    print("  4. Quitter")
    print("="*45)
    return input("Votre choix : ")

def main():
    print("Connexion au serveur...")
    try:
        envoyer("lister_matieres")
        print("✓ Connecté au serveur !")
    except Exception as e:
        print(f"✗ Erreur de connexion : {e}")
        sys.exit(1)

    etudiant_id = input("Votre ID étudiant (ex: ET001) : ")
    rep = envoyer("get_etudiant", {"id": etudiant_id})
    if not rep["ok"] or rep["data"] is None:
        print(f"✗ Étudiant {etudiant_id} introuvable.")
        sys.exit(1)
    infos = rep["data"]
    print(f"✓ Bienvenue {infos['prenom']} {infos['nom']} !")

    while True:
        choix = afficher_menu()

        if choix == "1":
            print("\n--- Mes Notes ---")
            rep = envoyer("get_notes_etudiant", {"etudiant_id": etudiant_id})
            if not rep["data"]:
                print("Aucune note enregistrée.")
            else:
                print(f"\n{'Matière':<25} {'Note':>6}  {'Professeur'}")
                print("-" * 50)
                for n in rep["data"]:
                    print(f"{n['matiere_nom']:<25} {n['valeur']:>5}/20  {n['professeur']}")

        elif choix == "2":
            print("\n--- Ma Moyenne ---")
            rep = envoyer("get_moyenne_etudiant", {"etudiant_id": etudiant_id})
            moyenne = rep["data"]
            print(f"✓ Moyenne générale : {moyenne}/20")
            if moyenne >= 10:
                print("  → Admis ✓")
            else:
                print("  → Ajourné ✗")

        elif choix == "3":
            print("\n--- Mon Bulletin ---")
            rep_infos   = envoyer("get_etudiant", {"id": etudiant_id})
            rep_notes   = envoyer("get_notes_etudiant", {"etudiant_id": etudiant_id})
            rep_moyenne = envoyer("get_moyenne_etudiant", {"etudiant_id": etudiant_id})
            infos   = rep_infos["data"]
            notes   = rep_notes["data"]
            moyenne = rep_moyenne["data"]
            print("=" * 50)
            print(f"  Nom     : {infos['prenom']} {infos['nom']}")
            print(f"  Filière : {infos['filiere']}")
            print("=" * 50)
            if not notes:
                print("  Aucune note enregistrée.")
            else:
                print(f"  {'Matière':<25} {'Note':>6}")
                print("  " + "-" * 35)
                for n in notes:
                    print(f"  {n['matiere_nom']:<25} {n['valeur']:>5}/20")
                print("  " + "-" * 35)
                print(f"  {'Moyenne générale':<25} {moyenne:>5}/20")
                print(f"  Décision : {'Admis ✓' if moyenne >= 10 else 'Ajourné ✗'}")
            print("=" * 50)

        elif choix == "4":
            print("Au revoir !")
            break

        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()