# server/database.py
import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'gestion_notes.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialiser_db():
    conn = get_connection()
    c = conn.cursor()

    # Facultés
    c.execute('''CREATE TABLE IF NOT EXISTS facultes (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        nom   TEXT UNIQUE NOT NULL
    )''')

    # Filières
    c.execute('''CREATE TABLE IF NOT EXISTS filieres (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        nom        TEXT NOT NULL,
        faculte_id INTEGER NOT NULL,
        FOREIGN KEY (faculte_id) REFERENCES facultes(id)
    )''')

    # Matières
    c.execute('''CREATE TABLE IF NOT EXISTS matieres (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        code        TEXT NOT NULL,
        nom         TEXT NOT NULL,
        coefficient INTEGER NOT NULL,
        niveau      INTEGER NOT NULL,
        semestre    INTEGER NOT NULL,
        filiere_id  INTEGER NOT NULL,
        FOREIGN KEY (filiere_id) REFERENCES filieres(id)
    )''')

    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role          TEXT NOT NULL,
        nom           TEXT NOT NULL,
        etudiant_id   TEXT,
        actif         INTEGER DEFAULT 1
    )''')

    # Étudiants
    c.execute('''CREATE TABLE IF NOT EXISTS etudiants (
        id         TEXT PRIMARY KEY,
        nom        TEXT NOT NULL,
        prenom     TEXT NOT NULL,
        filiere_id INTEGER NOT NULL,
        niveau     INTEGER NOT NULL,
        semestre   INTEGER NOT NULL,
        valide     INTEGER DEFAULT 0,
        FOREIGN KEY (filiere_id) REFERENCES filieres(id)
    )''')
    # Assignation prof → matière
    c.execute('''CREATE TABLE IF NOT EXISTS prof_matieres (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        matiere_id   INTEGER NOT NULL,
        FOREIGN KEY (user_id)    REFERENCES users(id),
        FOREIGN KEY (matiere_id) REFERENCES matieres(id)
    )''')

    # Notes
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id  TEXT NOT NULL,
        matiere_id   INTEGER NOT NULL,
        valeur       REAL NOT NULL,
        professeur   TEXT NOT NULL,
        UNIQUE(etudiant_id, matiere_id),
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
        FOREIGN KEY (matiere_id)  REFERENCES matieres(id)
    )''')

    conn.commit()

    # Compte admin par défaut
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        h = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        c.execute(
            "INSERT INTO users (username, password_hash, role, nom) VALUES (?,?,?,?)",
            ('admin', h, 'admin', 'Administrateur')
        )
        conn.commit()
        print("✓ Admin créé : admin / admin123")

    conn.close()

# ── Auth ───────────────────────────────────────────────────

def verifier_login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND actif=1", (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        return None
    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return dict(user)
    return None

def creer_user(username, password, role, nom, etudiant_id=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        h = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute(
            "INSERT INTO users (username,password_hash,role,nom,etudiant_id) VALUES (?,?,?,?,?)",
            (username, h, role, nom, etudiant_id)
        )
        conn.commit()
        return True, "Compte créé."
    except sqlite3.IntegrityError:
        return False, "Nom d'utilisateur déjà pris."
    finally:
        conn.close()

def lister_users(role=None):
    conn = get_connection()
    c = conn.cursor()
    if role:
        c.execute("SELECT id,username,role,nom,actif FROM users WHERE role=?", (role,))
    else:
        c.execute("SELECT id,username,role,nom,actif FROM users WHERE role != 'admin'")
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    return users

def supprimer_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ── Facultés ───────────────────────────────────────────────

def ajouter_faculte(nom):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO facultes (nom) VALUES (?)", (nom,))
        conn.commit()
        return True, "Faculté ajoutée."
    except sqlite3.IntegrityError:
        return False, "Faculté existe déjà."
    finally:
        conn.close()

def lister_facultes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM facultes")
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

def supprimer_faculte(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM facultes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Faculté supprimée."

# ── Filières ───────────────────────────────────────────────

def ajouter_filiere(nom, faculte_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO filieres (nom, faculte_id) VALUES (?,?)", (nom, faculte_id))
    conn.commit()
    conn.close()
    return True, "Filière ajoutée."

def lister_filieres(faculte_id=None):
    conn = get_connection()
    c = conn.cursor()
    if faculte_id:
        c.execute('''SELECT f.*, fa.nom as faculte_nom
                     FROM filieres f JOIN facultes fa ON f.faculte_id=fa.id
                     WHERE f.faculte_id=?''', (faculte_id,))
    else:
        c.execute('''SELECT f.*, fa.nom as faculte_nom
                     FROM filieres f JOIN facultes fa ON f.faculte_id=fa.id''')
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

def supprimer_filiere(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM filieres WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Filière supprimée."

# ── Matières ───────────────────────────────────────────────

def ajouter_matiere(code, nom, coefficient, niveau, semestre, filiere_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO matieres (code,nom,coefficient,niveau,semestre,filiere_id) VALUES (?,?,?,?,?,?)",
            (code, nom, coefficient, niveau, semestre, filiere_id)
        )
        conn.commit()
        return True, "Matière ajoutée."
    except:
        return False, "Erreur ajout matière."
    finally:
        conn.close()

def lister_matieres(filiere_id=None, niveau=None, semestre=None):
    conn = get_connection()
    c = conn.cursor()
    query = '''SELECT m.*, f.nom as filiere_nom
               FROM matieres m JOIN filieres f ON m.filiere_id=f.id
               WHERE 1=1'''
    params = []
    if filiere_id:
        query += " AND m.filiere_id=?"; params.append(filiere_id)
    if niveau:
        query += " AND m.niveau=?"; params.append(niveau)
    if semestre:
        query += " AND m.semestre=?"; params.append(semestre)
    c.execute(query, params)
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

def supprimer_matiere(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM matieres WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Matière supprimée."

# ── Étudiants ──────────────────────────────────────────────
def ajouter_etudiant(id, nom, prenom, filiere_id, niveau, semestre, valide=0):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO etudiants (id,nom,prenom,filiere_id,niveau,semestre,valide) VALUES (?,?,?,?,?,?,?)",
            (id, nom, prenom, filiere_id, niveau, semestre, valide)
        )
        conn.commit()
        return True, "Étudiant ajouté."
    except sqlite3.IntegrityError:
        return False, "Étudiant existe déjà."
    finally:
        conn.close()

def valider_etudiant(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE etudiants SET valide=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Étudiant validé."

def rejeter_etudiant(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM etudiants WHERE id=?", (id,))
    c.execute("DELETE FROM users WHERE etudiant_id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Étudiant rejeté."

def lister_etudiants(valide=None, filiere_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = '''SELECT e.*, f.nom as filiere_nom, fa.nom as faculte_nom
               FROM etudiants e
               JOIN filieres f  ON e.filiere_id = f.id
               JOIN facultes fa ON f.faculte_id  = fa.id
               WHERE 1=1'''
    params = []
    if valide is not None:
        query += " AND e.valide=?"
        params.append(valide)
    if filiere_id:
        query += " AND e.filiere_id=?"
        params.append(filiere_id)
    c.execute(query, params)
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

def get_etudiant(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT e.*, f.nom as filiere_nom, fa.nom as faculte_nom
                 FROM etudiants e
                 JOIN filieres f  ON e.filiere_id=f.id
                 JOIN facultes fa ON f.faculte_id=fa.id
                 WHERE e.id=?''', (id,))
    r = c.fetchone()
    conn.close()
    return dict(r) if r else None

def supprimer_etudiant(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM etudiants WHERE id=?", (id,))
    c.execute("DELETE FROM notes WHERE etudiant_id=?", (id,))
    c.execute("DELETE FROM users WHERE etudiant_id=?", (id,))
    conn.commit()
    conn.close()
    return True, "Étudiant supprimé."

def compter_etudiants():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM etudiants WHERE valide=1")
    n = c.fetchone()[0]
    conn.close()
    return n

# ── Professeurs ────────────────────────────────────────────

def assigner_matiere_prof(user_id, matiere_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO prof_matieres (user_id, matiere_id) VALUES (?,?)",
            (user_id, matiere_id)
        )
        conn.commit()
        return True, "Matière assignée."
    except sqlite3.IntegrityError:
        return False, "Déjà assigné."
    finally:
        conn.close()

def get_matieres_prof(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT m.*, f.nom as filiere_nom
                 FROM matieres m
                 JOIN prof_matieres pm ON m.id=pm.matiere_id
                 JOIN filieres f ON m.filiere_id=f.id
                 WHERE pm.user_id=?''', (user_id,))
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

# ── Notes ──────────────────────────────────────────────────

def ajouter_note(etudiant_id, matiere_id, valeur, professeur):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO notes (etudiant_id, matiere_id, valeur, professeur)
                     VALUES (?,?,?,?)
                     ON CONFLICT(etudiant_id, matiere_id)
                     DO UPDATE SET valeur=excluded.valeur, professeur=excluded.professeur''',
                  (etudiant_id, matiere_id, valeur, professeur))
        conn.commit()
        return True, f"Note {valeur}/20 enregistrée."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
def get_notes_etudiant(etudiant_id, semestre=None):
    conn = get_connection()
    c = conn.cursor()
    query = '''SELECT n.*, m.nom as matiere_nom, m.coefficient,
                      m.semestre, m.code
               FROM notes n
               JOIN matieres m ON n.matiere_id=m.id
               WHERE n.etudiant_id=?'''
    params = [etudiant_id]
    if semestre:
        query += " AND m.semestre=?"
        params.append(semestre)
    query += " ORDER BY m.semestre, m.nom"
    c.execute(query, params)
    r = [dict(x) for x in c.fetchall()]
    conn.close()
    return r

def get_moyenne_etudiant(etudiant_id):
    notes = get_notes_etudiant(etudiant_id)
    if not notes:
        return 0.0
    total = sum(n['valeur'] * n['coefficient'] for n in notes)
    coeffs = sum(n['coefficient'] for n in notes)
    return round(total / coeffs, 2)

def get_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM facultes")
    nb_facultes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM filieres")
    nb_filieres = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM etudiants WHERE valide=1")
    nb_etudiants = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='professeur'")
    nb_profs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM etudiants WHERE valide=0")
    nb_en_attente = c.fetchone()[0]
    conn.close()
    return {
        "facultes":    nb_facultes,
        "filieres":    nb_filieres,
        "etudiants":   nb_etudiants,
        "profs":       nb_profs,
        "en_attente":  nb_en_attente
    }
def avancer_semestre(etudiant_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT semestre, niveau FROM etudiants WHERE id=?", (etudiant_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Étudiant introuvable."
    nouveau_semestre = row['semestre'] + 1
    nouveau_niveau   = row['niveau']
    # Tous les 2 semestres = nouvelle année
    if nouveau_semestre % 2 == 1:
        nouveau_niveau += 1
    if nouveau_niveau > 5:
        conn.close()
        return False, "Niveau maximum atteint (Année 5)."
    c.execute(
        "UPDATE etudiants SET semestre=?, niveau=? WHERE id=?",
        (nouveau_semestre, nouveau_niveau, etudiant_id)
    )
    conn.commit()
    conn.close()
    return True, f"Passé au semestre {nouveau_semestre} — Année {nouveau_niveau}."