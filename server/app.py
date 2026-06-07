# server/app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import *

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)
app.secret_key = "gestion_notes_2026_secret"
initialiser_db()

# ── Helpers ────────────────────────────────────────────────

def login_requis(role=None):
    if 'user' not in session:
        return False
    if role and session['user']['role'] != role:
        return False
    return True

# ── Pages ──────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = verifier_login(request.form['username'], request.form['password'])
        if user:
            session['user'] = user
            return redirect(url_for(user['role']))
        return render_template('login.html', error="Identifiants incorrects.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    facultes = lister_facultes()
    filieres = lister_filieres()
    if request.method == 'POST':
        nom        = request.form['nom']
        prenom     = request.form['prenom']
        filiere_id = int(request.form['filiere_id'])
        semestre   = int(request.form['semestre'])
        password   = request.form['password']
        password2  = request.form['password2']

        if password != password2:
            return render_template('inscription.html',
                error="Les mots de passe ne correspondent pas.",
                facultes=facultes, filieres=filieres)

        # Génère ID automatique
        etudiants  = lister_etudiants()
        nouvel_id  = f"ET{len(etudiants) + 1:03d}"

       # Calcule le semestre selon le niveau
        niveau   = int(request.form['niveau'])
        semestre = (niveau - 1) * 2 + 1  # Année 1 → S1, Année 2 → S3, etc.

        ok, msg = ajouter_etudiant(nouvel_id, nom, prenom, filiere_id, niveau, semestre, valide=0)
        if not ok:
            return render_template('inscription.html',
                error=msg, facultes=facultes, filieres=filieres)

        creer_user(nouvel_id, password, 'etudiant', f"{prenom} {nom}", nouvel_id)

        return render_template('inscription.html',
            success=nouvel_id,
            facultes=facultes, filieres=filieres)

    return render_template('inscription.html',
        facultes=facultes, filieres=filieres)
@app.route('/admin')
def admin():
    if not login_requis('admin'):
        return redirect(url_for('login'))
    return render_template('admin.html', user=session['user'])

@app.route('/professeur')
def professeur():
    if not login_requis('professeur'):
        return redirect(url_for('login'))
    return render_template('professeur.html', user=session['user'])

@app.route('/etudiant')
def etudiant():
    if not login_requis('etudiant'):
        return redirect(url_for('login'))
    etud = get_etudiant(session['user']['etudiant_id'])
    if not etud or not etud['valide']:
        return render_template('attente.html')
    return render_template('etudiant.html', user=session['user'], etudiant=etud)

# ── API Stats ──────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

# ── API Facultés ───────────────────────────────────────────

@app.route('/api/facultes', methods=['GET'])
def api_lister_facultes():
    return jsonify(lister_facultes())

@app.route('/api/facultes', methods=['POST'])
def api_ajouter_faculte():
    data = request.json
    ok, msg = ajouter_faculte(data['nom'])
    return jsonify({"ok": ok, "message": msg})

@app.route('/api/facultes/<int:id>', methods=['DELETE'])
def api_supprimer_faculte(id):
    ok, msg = supprimer_faculte(id)
    return jsonify({"ok": ok, "message": msg})

# ── API Filières ───────────────────────────────────────────

@app.route('/api/filieres', methods=['GET'])
def api_lister_filieres():
    faculte_id = request.args.get('faculte_id')
    return jsonify(lister_filieres(faculte_id))

@app.route('/api/filieres', methods=['POST'])
def api_ajouter_filiere():
    data = request.json
    ok, msg = ajouter_filiere(data['nom'], data['faculte_id'])
    return jsonify({"ok": ok, "message": msg})

@app.route('/api/filieres/<int:id>', methods=['DELETE'])
def api_supprimer_filiere(id):
    ok, msg = supprimer_filiere(id)
    return jsonify({"ok": ok, "message": msg})

# ── API Matières ───────────────────────────────────────────

@app.route('/api/matieres', methods=['GET'])
def api_lister_matieres():
    filiere_id = request.args.get('filiere_id')
    niveau     = request.args.get('niveau')
    semestre   = request.args.get('semestre')
    return jsonify(lister_matieres(filiere_id, niveau, semestre))

@app.route('/api/matieres', methods=['POST'])
def api_ajouter_matiere():
    data = request.json
    ok, msg = ajouter_matiere(
        data['code'], data['nom'], data['coefficient'],
        data['niveau'], data['semestre'], data['filiere_id']
    )
    return jsonify({"ok": ok, "message": msg})
@app.route('/api/matieres/<int:id>', methods=['DELETE'])
def api_supprimer_matiere(id):
    ok, msg = supprimer_matiere(id)
    return jsonify({"ok": ok, "message": msg})

# ── API Étudiants ──────────────────────────────────────────

@app.route('/api/etudiants', methods=['GET'])
def api_lister_etudiants():
    valide     = request.args.get('valide')
    filiere_id = request.args.get('filiere_id')
    if valide is not None:
        valide = int(valide)
    return jsonify(lister_etudiants(valide, filiere_id))

@app.route('/api/etudiants/<id>/valider', methods=['POST'])
def api_valider_etudiant(id):
    ok, msg = valider_etudiant(id)
    return jsonify({"ok": ok, "message": msg})

@app.route('/api/etudiants/<id>/rejeter', methods=['POST'])
def api_rejeter_etudiant(id):
    ok, msg = rejeter_etudiant(id)
    return jsonify({"ok": ok, "message": msg})
@app.route('/api/etudiants/<id>/avancer', methods=['POST'])
def api_avancer_semestre(id):
    ok, msg = avancer_semestre(id)
    return jsonify({"ok": ok, "message": msg})

@app.route('/api/etudiants/<id>', methods=['DELETE'])
def api_supprimer_etudiant(id):
    ok, msg = supprimer_etudiant(id)
    return jsonify({"ok": ok, "message": msg})

# ── API Professeurs ────────────────────────────────────────

@app.route('/api/professeurs', methods=['GET'])
def api_lister_professeurs():
    return jsonify(lister_users('professeur'))

@app.route('/api/professeurs', methods=['POST'])
def api_ajouter_professeur():
    data = request.json
    ok, msg = creer_user(
        data['username'], data['password'],
        'professeur', data['nom']
    )
    return jsonify({"ok": ok, "message": msg})

@app.route('/api/professeurs/<username>', methods=['DELETE'])
def api_supprimer_professeur(username):
    supprimer_user(username)
    return jsonify({"ok": True, "message": "Professeur supprimé."})

@app.route('/api/professeurs/<int:user_id>/matieres', methods=['GET'])
def api_get_matieres_prof(user_id):
    return jsonify(get_matieres_prof(user_id))

@app.route('/api/professeurs/<int:user_id>/matieres', methods=['POST'])
def api_assigner_matiere(user_id):
    data = request.json
    ok, msg = assigner_matiere_prof(user_id, data['matiere_id'])
    return jsonify({"ok": ok, "message": msg})

# ── API Notes ──────────────────────────────────────────────

@app.route('/api/notes', methods=['POST'])
def api_ajouter_note():
    data = request.json
    ok, msg = ajouter_note(
        data['etudiant_id'], data['matiere_id'],
        data['valeur'], data['professeur']
    )
    return jsonify({"ok": ok, "message": msg})
@app.route('/api/notes/<etudiant_id>', methods=['GET'])
def api_get_notes(etudiant_id):
    semestre = request.args.get('semestre')
    return jsonify(get_notes_etudiant(etudiant_id, semestre))
@app.route('/api/moyenne/<etudiant_id>', methods=['GET'])
def api_get_moyenne(etudiant_id):
    semestre = request.args.get('semestre')
    notes = get_notes_etudiant(etudiant_id, int(semestre) if semestre else None)
    if not notes:
        return jsonify({"moyenne": 0.0})
    total  = sum(n['valeur'] * n['coefficient'] for n in notes)
    coeffs = sum(n['coefficient'] for n in notes)
    return jsonify({"moyenne": round(total / coeffs, 2)})
# ── Démarrage ──────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 50)
    print("  SERVEUR WEB — GESTION DE NOTES")
    print("  http://127.0.0.1:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)
