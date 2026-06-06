# server/gestion_notes.py
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import Etudiant, Note, Matiere

FICHIER_DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'notes.json')

class GestionNotes:

    def __init__(self):
        self.etudiants = {}
        self.matieres  = {}
        self._charger_donnees()
        self._initialiser_matieres()

    def _initialiser_matieres(self):
        if not self.matieres:
            for m in [
                Matiere("MATH101", "Mathématiques",     3),
                Matiere("INFO102", "Algorithmique",      3),
                Matiere("PHYS103", "Physique",           2),
                Matiere("ANGL104", "Anglais",            1),
                Matiere("RESX105", "Systèmes Répartis",  3),
            ]:
                self.matieres[m.code] = m
            self._sauvegarder_donnees()

    # ── Étudiants ──────────────────────────────────────────

    def ajouter_etudiant(self, id, nom, prenom, filiere):
        if id in self.etudiants:
            return False, f"Étudiant {id} existe déjà."
        self.etudiants[id] = Etudiant(id, nom, prenom, filiere)
        self._sauvegarder_donnees()
        return True, f"Étudiant {prenom} {nom} ajouté."

    def supprimer_etudiant(self, id):
        if id not in self.etudiants:
            return False, f"Étudiant {id} introuvable."
        del self.etudiants[id]
        self._sauvegarder_donnees()
        return True, f"Étudiant {id} supprimé."

    def lister_etudiants(self):
        return [e.to_dict() for e in self.etudiants.values()]

    def get_etudiant(self, id):
        if id not in self.etudiants:
            return None
        e = self.etudiants[id]
        return {"id": e.id, "nom": e.nom, "prenom": e.prenom, "filiere": e.filiere}

    # ── Notes ──────────────────────────────────────────────

    def ajouter_note(self, etudiant_id, matiere_code, valeur, professeur):
        if etudiant_id not in self.etudiants:
            return False, f"Étudiant {etudiant_id} introuvable."
        if matiere_code not in self.matieres:
            return False, f"Matière {matiere_code} introuvable."
        if not (0 <= valeur <= 20):
            return False, "La note doit être entre 0 et 20."
        note = Note(etudiant_id, matiere_code, valeur, professeur)
        self.etudiants[etudiant_id].ajouter_note(note)
        self._sauvegarder_donnees()
        return True, f"Note {valeur}/20 ajoutée."

    def get_notes_etudiant(self, etudiant_id):
        if etudiant_id not in self.etudiants:
            return None
        e = self.etudiants[etudiant_id]
        return [
            {
                "matiere_code": n.matiere_code,
                "matiere_nom":  self.matieres[n.matiere_code].nom
                                if n.matiere_code in self.matieres else n.matiere_code,
                "valeur":       n.valeur,
                "professeur":   n.professeur
            }
            for n in e.notes
        ]

    def get_moyenne_etudiant(self, etudiant_id):
        if etudiant_id not in self.etudiants:
            return None
        e = self.etudiants[etudiant_id]
        return e.calculer_moyenne(list(self.matieres.values()))

    def lister_matieres(self):
        return [m.to_dict() for m in self.matieres.values()]

    # ── Persistance ────────────────────────────────────────

    def _sauvegarder_donnees(self):
        data = {
            "matieres":  [m.to_dict() for m in self.matieres.values()],
            "etudiants": [e.to_dict() for e in self.etudiants.values()]
        }
        with open(FICHIER_DATA, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _charger_donnees(self):
        if not os.path.exists(FICHIER_DATA):
            return
        try:
            with open(FICHIER_DATA, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for m in data.get("matieres", []):
                self.matieres[m["code"]] = Matiere.from_dict(m)
            for e in data.get("etudiants", []):
                self.etudiants[e["id"]] = Etudiant.from_dict(e)
        except Exception as ex:
            print(f"Erreur chargement : {ex}")