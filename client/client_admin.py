# client/client_admin.py
import socket
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HOST = "127.0.0.1"
PORT = 5000

def envoyer(action, params={}):
    """Envoie une requête au serveur et retourne la réponse"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        requete = json.dumps({"action": action, "params": params})
        s.send(requete.encode('utf-8'))
        reponse = s.recv(4096).decode('utf-8')
        return json.loads(reponse)

def afficher_menu():
    print("\n" + "="*45)
    print("   INTERFACE ADMIN — Gestion des Étudiants")
    print("="*45)
    print("  1. Ajouter un étudiant")
    print("  2. Supprimer un étudiant")
    print("  3. Lister tous les étudiants")
    print("  4. Quitter")
    print("="*45)
    return input("Votre choix : ")

def main():
    print("Connexion au serveur...")
    try:
        rep = envoyer("lister_etudiants")
        print("✓ Connecté au serveur !")
    except Exception as e:
        print(f"✗ Erreur de connexion : {e}")
        sys.exit(1)

    while True:
        choix = afficher_menu()

        if choix == "1":
            print("\n--- Ajouter un étudiant ---")
            id      = input("ID (ex: ET001) : ")
            nom     = input("Nom : ")
            prenom  = input("Prénom : ")
            filiere = input("Filière : ")
            rep = envoyer("ajouter_etudiant", {
                "id": id, "nom": nom,
                "prenom": prenom, "filiere": filiere
            })
            print(f"{'✓' if rep['ok'] else '✗'} {rep['message']}")

        elif choix == "2":
            print("\n--- Supprimer un étudiant ---")
            id  = input("ID étudiant : ")
            rep = envoyer("supprimer_etudiant", {"id": id})
            print(f"{'✓' if rep['ok'] else '✗'} {rep['message']}")

        elif choix == "3":
            print("\n--- Liste des étudiants ---")
            rep = envoyer("lister_etudiants")
            etudiants = rep["data"]
            if not etudiants:
                print("Aucun étudiant enregistré.")
            else:
                print(f"\n{'ID':<8} {'Nom':<15} {'Prénom':<15} {'Filière'}")
                print("-" * 55)
                for e in etudiants:
                    print(f"{e['id']:<8} {e['nom']:<15} {e['prenom']:<15} {e['filiere']}")

        elif choix == "4":
            print("Au revoir !")
            break

        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()