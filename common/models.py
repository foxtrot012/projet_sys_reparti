# common/models.py

class Matiere:
    def __init__(self, code, nom, coefficient):
        self.code        = code
        self.nom         = nom
        self.coefficient = coefficient

    def to_dict(self):
        return {
            "code":        self.code,
            "nom":         self.nom,
            "coefficient": self.coefficient
        }

    @staticmethod
    def from_dict(d):
        return Matiere(d["code"], d["nom"], d["coefficient"])


class Note:
    def __init__(self, etudiant_id, matiere_code, valeur, professeur):
        self.etudiant_id  = etudiant_id
        self.matiere_code = matiere_code
        self.valeur       = valeur
        self.professeur   = professeur

    def to_dict(self):
        return {
            "etudiant_id":  self.etudiant_id,
            "matiere_code": self.matiere_code,
            "valeur":       self.valeur,
            "professeur":   self.professeur
        }

    @staticmethod
    def from_dict(d):
        return Note(
            d["etudiant_id"],
            d["matiere_code"],
            d["valeur"],
            d["professeur"]
        )


class Etudiant:
    def __init__(self, id, nom, prenom, filiere):
        self.id      = id
        self.nom     = nom
        self.prenom  = prenom
        self.filiere = filiere
        self.notes   = []

    def ajouter_note(self, note):
        for i, n in enumerate(self.notes):
            if n.matiere_code == note.matiere_code:
                self.notes[i] = note
                return
        self.notes.append(note)

    def calculer_moyenne(self, matieres):
        if not self.notes:
            return 0.0
        coeffs       = {m.code: m.coefficient for m in matieres}
        total_points = 0
        total_coeffs = 0
        for note in self.notes:
            coeff         = coeffs.get(note.matiere_code, 1)
            total_points += note.valeur * coeff
            total_coeffs += coeff
        return round(total_points / total_coeffs, 2)

    def to_dict(self):
        return {
            "id":      self.id,
            "nom":     self.nom,
            "prenom":  self.prenom,
            "filiere": self.filiere,
            "notes":   [n.to_dict() for n in self.notes]
        }

    @staticmethod
    def from_dict(d):
        e = Etudiant(d["id"], d["nom"], d["prenom"], d["filiere"])
        for n in d.get("notes", []):
            e.notes.append(Note.from_dict(n))
        return e