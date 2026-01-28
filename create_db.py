import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# --- 1. Insertion des CLIENTS (Ton code existant) ---
print("Ajout des clients...")
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('DUPONT', 'Emilie', '123, Rue des Lilas, 75001 Paris'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LEROUX', 'Lucas', '456, Avenue du Soleil, 31000 Toulouse'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('MARTIN', 'Amandine', '789, Rue des Érables, 69002 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('TREMBLAY', 'Antoine', '1010, Boulevard de la Mer, 13008 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LAMBERT', 'Sarah', '222, Avenue de la Liberté, 59000 Lille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('GAGNON', 'Nicolas', '456, Boulevard des Cerisiers, 69003 Lyon'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('DUBOIS', 'Charlotte', '789, Rue des Roses, 13005 Marseille'))
cur.execute("INSERT INTO clients (nom, prenom, adresse) VALUES (?, ?, ?)",('LEFEVRE', 'Thomas', '333, Rue de la Paix, 75002 Paris'))

# --- 2. Insertion des LIVRES (Nouveauté Séquence 6) ---
print("Ajout des livres...")
cur.execute("INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)", ('Harry Potter à l\'école des sorciers', 'J.K. Rowling', 3))
cur.execute("INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)", ('Le Seigneur des Anneaux', 'J.R.R. Tolkien', 1))
cur.execute("INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)", ('1984', 'George Orwell', 5))
cur.execute("INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)", ('Les Misérables', 'Victor Hugo', 0))
cur.execute("INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)", ('Le Petit Prince', 'Antoine de Saint-Exupéry', 2))

connection.commit()
connection.close()

print("Terminé ! La base de données contient maintenant Clients + Livres.")
