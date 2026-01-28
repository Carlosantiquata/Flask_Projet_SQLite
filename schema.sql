DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    adresse TEXT NOT NULL
);
/* --- Partie Bibliothèque (Séquence 6) --- */

DROP TABLE IF EXISTS livres;
DROP TABLE IF EXISTS emprunts;

/* 1. La table des livres avec gestion du stock */
CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 1  /* Important pour l'exercice ! */
);

/* 2. La table de liaison (Qui a emprunté Quoi ?) */
CREATE TABLE emprunts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livre_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,  /* On lie ça à l'ID de ta table 'clients' */
    date_emprunt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_retour TIMESTAMP,       /* Sera rempli quand le livre revient */
    FOREIGN KEY (livre_id) REFERENCES livres (id),
    FOREIGN KEY (client_id) REFERENCES clients (id)
);

/* --- Quelques données pour tester tout de suite --- */

/* On ajoute des livres */
INSERT INTO livres (titre, auteur, stock) VALUES ('Harry Potter', 'J.K. Rowling', 3);
INSERT INTO livres (titre, auteur, stock) VALUES ('Le Seigneur des Anneaux', 'J.R.R. Tolkien', 1);
INSERT INTO livres (titre, auteur, stock) VALUES ('Les Misérables', 'Victor Hugo', 0); /* Stock 0 = indisponible */

/* On ajoute un client test (si tu n'en as pas déjà) */
INSERT INTO clients (nom, prenom, adresse) VALUES ('Dupont', 'Jean', '1 rue de la Paix');
