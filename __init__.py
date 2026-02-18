from flask import Flask, render_template, request, redirect, url_for, session, jsonify, render_template_string
import sqlite3
import os  # <--- NOUVEAU : Ajoute cette ligne !

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# --- CORRECTION DU PROBLÈME DE BASE DE DONNÉES VIDE ---
def get_db_connection():
    # On calcule le chemin ABSOLU du fichier (l'adresse exacte sur le disque)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'database.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================
#             GESTION AUTHENTIFICATION
# =========================================================

# Vérifie si l'utilisateur est connecté
def is_logged_in():
    return 'user_id' in session

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
            # On redirige vers l'accueil (Dashboard)
            return redirect(url_for('hello_world'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello_world'))


# =========================================================
#                    PAGES CLIENTS (Consultation)
# =========================================================

@app.route('/')
def hello_world():
    # On envoie des infos à la page d'accueil pour le tableau de bord
    conn = get_db_connection()
    livres = conn.execute("SELECT * FROM livres LIMIT 3").fetchall()
    
    taches = []
    if is_logged_in():
        taches = conn.execute("SELECT * FROM taches WHERE utilisateur_id=? AND terminee=0 LIMIT 3", 
                             (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('hello.html', livres=livres, taches=taches)

@app.route('/consultation/')
def ReadBDD():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM clients;').fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_nom/', methods=['GET'])
def fiche_nom():
    if not is_logged_in():
        return redirect(url_for('authentification'))

    nom = request.args.get('nom', '').strip()
    if nom == "":
        return render_template_string("""
        <!doctype html>
        <html><body>
            <h2>Recherche client</h2>
            <form action="/fiche_nom/"><input name="nom"><button>Chercher</button></form>
        </body></html>
        """)
    
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM clients WHERE nom LIKE ?", (f"%{nom}%",)).fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET', 'POST'])
def enregistrer_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        conn = get_db_connection()
        conn.execute('INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)', (nom, prenom, "Inconnue"))
        conn.commit()
        conn.close()
        return redirect('/consultation/')
    return render_template('formulaire.html')


# =========================================================
#           GESTIONNAIRE DE TÂCHES
# =========================================================

@app.route('/taches')
def taches():
    if not is_logged_in():
        return redirect(url_for('authentification'))

    conn = get_db_connection()
    # On récupère les tâches de l'utilisateur
    mes_taches = conn.execute("""
        SELECT * FROM taches 
        WHERE utilisateur_id=? 
        ORDER BY terminee ASC, date_echeance ASC
    """, (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('taches.html', taches=mes_taches)

@app.route('/taches/ajouter', methods=['POST'])
def ajouter_tache():
    if not is_logged_in():
        return redirect(url_for('authentification'))

    titre = request.form.get('titre')
    description = request.form.get('description')
    date_echeance = request.form.get('date_echeance')

    if titre:
        conn = get_db_connection()
        conn.execute("INSERT INTO taches (utilisateur_id, titre, description, date_echeance) VALUES (?, ?, ?, ?)",
                     (session['user_id'], titre, description, date_echeance))
        conn.commit()
        conn.close()
    return redirect(url_for('taches'))

@app.route('/taches/terminer/<int:tache_id>', methods=['POST'])
def toggle_terminee(tache_id):
    if not is_logged_in():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    row = conn.execute("SELECT terminee FROM taches WHERE id=? AND utilisateur_id=?", 
                       (tache_id, session['user_id'])).fetchone()
    if row:
        new_val = 0 if row['terminee'] else 1
        conn.execute("UPDATE taches SET terminee=? WHERE id=?", (new_val, tache_id))
        conn.commit()
    conn.close()
    return redirect(url_for('taches'))

@app.route('/taches/supprimer/<int:tache_id>', methods=['POST'])
def supprimer_tache(tache_id):
    if not is_logged_in():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    conn.execute("DELETE FROM taches WHERE id=? AND utilisateur_id=?", (tache_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('taches'))


# =========================================================
#             BIBLIOTHEQUE (INTERFACE VISUELLE)
# =========================================================

# 1. Page principale de la bibliothèque (Recherche + Liste)
@app.route('/bibliotheque')
def bibliotheque():
    # Protection : il faut être connecté
    if not is_logged_in():
        return redirect(url_for('authentification'))
    
    conn = get_db_connection()
    q = request.args.get('q', '').strip()
    
    if q:
        # Recherche par titre ou auteur
        livres = conn.execute("SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ?", 
                             (f"%{q}%", f"%{q}%")).fetchall()
    else:
        # Sinon on affiche tout
        livres = conn.execute("SELECT * FROM livres").fetchall()
    
    conn.close()
    return render_template('biblio.html', livres=livres)

# 2. Action d'emprunter un livre (Via bouton HTML)
@app.route('/emprunter/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not is_logged_in():
        return redirect(url_for('authentification'))
        
    conn = get_db_connection()
    livre = conn.execute("SELECT stock_disponible FROM livres WHERE id=?", (livre_id,)).fetchone()
    
    # Vérification du stock
    if livre and livre['stock_disponible'] > 0:
        # Mise à jour du stock (-1)
        conn.execute("UPDATE livres SET stock_disponible = stock_disponible - 1 WHERE id=?", (livre_id,))
        # Création de l'emprunt
        conn.execute("INSERT INTO emprunts (utilisateur_id, livre_id, statut) VALUES (?, ?, 'EN_COURS')",
                     (session['user_id'], livre_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('bibliotheque'))

# 3. Action de supprimer un livre (ADMIN SEULEMENT)
@app.route('/admin/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre_admin(livre_id):
    if not is_logged_in() or session.get('role') != 'admin':
        return "Accès refusé. Réservé aux administrateurs.", 403
        
    conn = get_db_connection()
    conn.execute("DELETE FROM livres WHERE id=?", (livre_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('bibliotheque'))

# =========================================================
#                        LANCEMENT
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
