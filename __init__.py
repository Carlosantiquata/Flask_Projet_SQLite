from flask import Flask, render_template, request, redirect, url_for, session, jsonify, render_template_string
import sqlite3
import os  # <--- INDISPENSABLE pour le GPS

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# --- 1. LE GPS (Chemin Absolu) ---
def get_db_path():
    # Trouve le dossier où se trouve CE fichier __init__.py
    basedir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(basedir, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

# --- UTILITAIRES ---
def is_logged_in():
    return 'user_id' in session

# =========================================================
#                 AUTHENTIFICATION
# =========================================================

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM utilisateurs WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('hello_world'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_world'))

# =========================================================
#                 ACCUEIL (Tableau de bord)
# =========================================================

@app.route('/')
def hello_world():
    conn = get_db_connection()
    # On envoie les livres et les tâches pour que le dashboard fonctionne
    try:
        livres = conn.execute("SELECT * FROM livres LIMIT 3").fetchall()
    except:
        livres = [] # Si la table n'existe pas encore
        
    taches = []
    if is_logged_in():
        try:
            taches = conn.execute("SELECT * FROM taches WHERE utilisateur_id=? AND terminee=0 LIMIT 3", 
                                 (session['user_id'],)).fetchall()
        except:
            pass
    
    conn.close()
    return render_template('hello.html', livres=livres, taches=taches)

# =========================================================
#                 GESTION DES TÂCHES
# =========================================================

@app.route('/taches')
def taches():
    if not is_logged_in(): return redirect(url_for('authentification'))
    conn = get_db_connection()
    mes_taches = conn.execute("SELECT * FROM taches WHERE utilisateur_id=? ORDER BY terminee ASC, date_echeance ASC", 
                              (session['user_id'],)).fetchall()
    conn.close()
    return render_template('taches.html', taches=mes_taches)

@app.route('/taches/ajouter', methods=['POST'])
def ajouter_tache():
    if not is_logged_in(): return redirect(url_for('authentification'))
    titre = request.form.get('titre')
    date_echeance = request.form.get('date_echeance')
    if titre:
        conn = get_db_connection()
        conn.execute("INSERT INTO taches (utilisateur_id, titre, description, date_echeance, terminee) VALUES (?, ?, '', ?, 0)",
                     (session['user_id'], titre, date_echeance))
        conn.commit()
        conn.close()
    return redirect(url_for('taches'))

@app.route('/taches/terminer/<int:tache_id>', methods=['POST'])
def toggle_terminee(tache_id):
    if not is_logged_in(): return redirect(url_for('authentification'))
    conn = get_db_connection()
    row = conn.execute("SELECT terminee FROM taches WHERE id=? AND utilisateur_id=?", (tache_id, session['user_id'])).fetchone()
    if row:
        new_val = 0 if row['terminee'] == 1 else 1
        conn.execute("UPDATE taches SET terminee=? WHERE id=?", (new_val, tache_id))
        conn.commit()
    conn.close()
    return redirect(url_for('taches'))

@app.route('/taches/supprimer/<int:tache_id>', methods=['POST'])
def supprimer_tache(tache_id):
    if not is_logged_in(): return redirect(url_for('authentification'))
    conn = get_db_connection()
    conn.execute("DELETE FROM taches WHERE id=? AND utilisateur_id=?", (tache_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('taches'))

# =========================================================
#                 BIBLIOTHÈQUE (Sequence 6)
# =========================================================

@app.route('/bibliotheque')
def bibliotheque():
    if not is_logged_in(): return redirect(url_for('authentification'))
    conn = get_db_connection()
    q = request.args.get('q', '').strip()
    if q:
        livres = conn.execute("SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?", (f"%{q}%", f"%{q}%")).fetchall()
    else:
        livres = conn.execute("SELECT * FROM livres").fetchall()
    conn.close()
    return render_template('biblio.html', livres=livres)

@app.route('/emprunter/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not is_logged_in(): return redirect(url_for('authentification'))
    conn = get_db_connection()
    livre = conn.execute("SELECT stock_disponible FROM livres WHERE id=?", (livre_id,)).fetchone()
    if livre and livre['stock_disponible'] > 0:
        conn.execute("UPDATE livres SET stock_disponible = stock_disponible - 1 WHERE id=?", (livre_id,))
        conn.execute("INSERT INTO emprunts (utilisateur_id, livre_id, statut) VALUES (?, ?, 'EN_COURS')",
                     (session['user_id'], livre_id))
        conn.commit()
    conn.close()
    return redirect(url_for('bibliotheque'))

@app.route('/admin/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre_admin(livre_id):
    if not is_logged_in() or session.get('role') != 'admin':
        return "Accès interdit", 403
    conn = get_db_connection()
    conn.execute("DELETE FROM livres WHERE id=?", (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('bibliotheque'))

# =========================================================
#                 CLIENTS (Ancien)
# =========================================================
@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM clients;').fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)', (request.form['nom'], request.form['prenom'], "Inconnue"))
        conn.commit()
        conn.close()
        return redirect('/consultation/')
    return render_template('formulaire.html')

@app.route('/fiche_nom/', methods=['GET'])
def fiche_nom():
    if not is_logged_in(): return redirect(url_for('authentification'))
    nom = request.args.get('nom', '').strip()
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM clients WHERE nom LIKE ?", (f"%{nom}%",)).fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# =========================================================
#                 🚨 ZONE DEBUG / ESPION 🚨
# =========================================================
@app.route('/debug')
def debug_page():
    # 1. Où sommes-nous ?
    dossier_actuel = os.path.abspath(os.path.dirname(__file__))
    
    # 2. Où est la base de données ?
    db_path = get_db_path()
    db_existe = os.path.exists(db_path)
    
    # 3. Qu'y a-t-il dedans ?
    status = ""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Compter les livres
        cur.execute("SELECT count(*) FROM livres")
        nb_livres = cur.fetchone()[0]
        
        # Compter les utilisateurs
        cur.execute("SELECT count(*) FROM utilisateurs")
        nb_users = cur.fetchone()[0]
        
        status = f"✅ Connexion OK.<br>Livres trouvés : {nb_livres}<br>Utilisateurs trouvés : {nb_users}"
        conn.close()
    except Exception as e:
        status = f"❌ Erreur lecture base : {str(e)}"

    html = f"""
    <div style="font-family: sans-serif; padding: 20px; border: 2px solid red; background: #fff0f0;">
        <h1>🕵️ Rapport d'Enquête</h1>
        <p><b>Dossier du site (GPS) :</b> {dossier_actuel}</p>
        <p><b>Chemin Base de données :</b> {db_path}</p>
        <p><b>Le fichier existe ?</b> {'✅ OUI' if db_existe else '❌ NON'}</p>
        <hr>
        <p><b>Contenu :</b> {status}</p>
    </div>
    """
    return html

# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
