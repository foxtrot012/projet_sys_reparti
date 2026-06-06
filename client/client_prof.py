# client/client_prof.py
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
    print("   INTERFACE PROFESSEUR — Gestion des Notes")
    print("="*45)
    print("  1. Ajouter / Modifier une note")
    print("  2. Voir les notes d'un étudiant")
    print("  3. Voir la moyenne d'un étudiant")
    print("  4. Lister les matières")
    print("  5. Quitter")
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

    nom_prof = input("Votre nom (ex: Prof. Diallo) : ")

    while True:
        choix = afficher_menu()

        if choix == "1":
            print("\n--- Ajouter une note ---")
            # Affiche les matières disponibles
            rep = envoyer("lister_matieres")
            print("Matières disponibles :")
            for m in rep["data"]:
                print(f"  {m['code']} — {m['nom']}")
            etudiant_id  = input("ID étudiant : ")
            matiere_code = input("Code matière : ")
            try:
                valeur = float(input("Note (/20) : "))
            except ValueError:
                print("✗ Note invalide.")
                continue
            rep = envoyer("ajouter_note", {
                "etudiant_id":  etudiant_id,
                "matiere_code": matiere_code,
                "valeur":       valeur,
                "professeur":   nom_prof
            })
            print(f"{'✓' if rep['ok'] else '✗'} {rep['message']}")

        elif choix == "2":
            print("\n--- Notes d'un étudiant ---")
            etudiant_id = input("ID étudiant : ")
            rep = envoyer("get_notes_etudiant", {"etudiant_id": etudiant_id})
            if not rep["ok"]:
                print("✗ Étudiant introuvable.")
            elif not rep["data"]:
                print("Aucune note enregistrée.")
            else:
                print(f"\n{'Matière':<25} {'Note':>6}  {'Professeur'}")
                print("-" * 50)
                for n in rep["data"]:
                    print(f"{n['matiere_nom']:<25} {n['valeur']:>5}/20  {n['professeur']}")

        elif choix == "3":
            print("\n--- Moyenne d'un étudiant ---")
            etudiant_id = input("ID étudiant : ")
            rep = envoyer("get_moyenne_etudiant", {"etudiant_id": etudiant_id})
            if not rep["ok"]:
                print("✗ Étudiant introuvable.")
            else:
                print(f"✓ Moyenne : {rep['data']}/20")

        elif choix == "4":
            print("\n--- Liste des matières ---")
            rep = envoyer("lister_matieres")
            print(f"\n{'Code':<10} {'Nom':<25} {'Coeff'}")
            print("-" * 40)
            for m in rep["data"]:
                print(f"{m['code']:<10} {m['nom']:<25} {m['coefficient']}")

        elif choix == "5":
            print("Au revoir !")
            break

        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()