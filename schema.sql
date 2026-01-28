DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    adresse TEXT NOT NULL
);
/* Ajout pour la bibliothèque */
DROP TABLE IF EXISTS livres;

CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 1
);

/* On ajoute quelques livres pour que la page ne soit pas vide */
INSERT INTO livres (titre, auteur, stock) VALUES ('Harry Potter', 'J.K. Rowling', 3);
INSERT INTO livres (titre, auteur, stock) VALUES ('Le Petit Prince', 'Saint-Exupéry', 5);
INSERT INTO livres (titre, auteur, stock) VALUES ('Misérables', 'Victor Hugo', 0);
