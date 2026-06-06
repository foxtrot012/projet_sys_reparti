# server/serveur.py
import socket
import threading
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.gestion_notes import GestionNotes

HOST = "127.0.0.1"
PORT = 5000

gestion = GestionNotes()

def traiter_requete(data):
    """Reçoit une requête JSON et retourne une réponse JSON"""
    try:
        requete = json.loads(data)
        action  = requete.get("action")
        params  = requete.get("params", {})

        # ── Étudiants ──────────────────────────────
        if action == "ajouter_etudiant":
            ok, msg = gestion.ajouter_etudiant(
                params["id"], params["nom"],
                params["prenom"], params["filiere"]
            )
            return {"ok": ok, "message": msg}

        elif action == "supprimer_etudiant":
            ok, msg = gestion.supprimer_etudiant(params["id"])
            return {"ok": ok, "message": msg}

        elif action == "lister_etudiants":
            return {"ok": True, "data": gestion.lister_etudiants()}

        elif action == "get_etudiant":
            data = gestion.get_etudiant(params["id"])
            return {"ok": data is not None, "data": data}

        # ── Notes ──────────────────────────────────
        elif action == "ajouter_note":
            ok, msg = gestion.ajouter_note(
                params["etudiant_id"], params["matiere_code"],
                params["valeur"],     params["professeur"]
            )
            return {"ok": ok, "message": msg}

        elif action == "get_notes_etudiant":
            data = gestion.get_notes_etudiant(params["etudiant_id"])
            return {"ok": data is not None, "data": data}

        elif action == "get_moyenne_etudiant":
            moyenne = gestion.get_moyenne_etudiant(params["etudiant_id"])
            return {"ok": moyenne is not None, "data": moyenne}

        elif action == "lister_matieres":
            return {"ok": True, "data": gestion.lister_matieres()}

        else:
            return {"ok": False, "message": f"Action inconnue : {action}"}

    except Exception as e:
        return {"ok": False, "message": f"Erreur serveur : {str(e)}"}


def gerer_client(conn, addr):
    """Gère un client connecté dans un thread séparé"""
    print(f"  → Client connecté : {addr}")
    try:
        while True:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break
            reponse = traiter_requete(data)
            conn.send(json.dumps(reponse).encode('utf-8'))
    except Exception as e:
        print(f"  → Erreur client {addr} : {e}")
    finally:
        conn.close()
        print(f"  → Client déconnecté : {addr}")


def demarrer_serveur():
    """Démarre le serveur socket"""
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind((HOST, PORT))
    serveur.listen(5)

    print("=" * 50)
    print("  SERVEUR GESTION DE NOTES")
    print(f"  Écoute sur {HOST}:{PORT}")
    print("  (Ctrl+C pour arrêter)")
    print("=" * 50)

    try:
        while True:
            conn, addr = serveur.accept()
            thread = threading.Thread(
                target=gerer_client,
                args=(conn, addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
    finally:
        serveur.close()


if __name__ == "__main__":
    demarrer_serveur()