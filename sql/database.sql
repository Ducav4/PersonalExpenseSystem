-- Creazione tabelle per il progetto spese

-- Tabella Categorie
-- Uso id autoincrementante e nome univoco
CREATE TABLE IF NOT EXISTS Categorie (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_categoria TEXT NOT NULL UNIQUE
);

-- Tabella Spese
-- Controllo che l'importo sia positivo
CREATE TABLE IF NOT EXISTS Spese (
    id_spesa INTEGER PRIMARY KEY AUTOINCREMENT,
    data_spesa TEXT NOT NULL,
    importo REAL NOT NULL CHECK (importo > 0),
    descrizione TEXT,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria)
);

-- Tabella Budget
-- Un solo budget per categoria ogni mese
CREATE TABLE IF NOT EXISTS Budget (
    id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
    mese_anno TEXT NOT NULL,
    importo_budget REAL NOT NULL CHECK (importo_budget > 0),
    id_categoria INTEGER NOT NULL,
    UNIQUE (mese_anno, id_categoria),
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria)
);

-- Dati iniziali di prova
INSERT INTO Categorie (nome_categoria) VALUES ('Alimentari');
INSERT INTO Categorie (nome_categoria) VALUES ('Trasporti');
INSERT INTO Categorie (nome_categoria) VALUES ('Svago');

INSERT INTO Spese (data_spesa, importo, descrizione, id_categoria) 
VALUES ('2026-02-10', 45.50, 'Spesa Supermercato', 1);

INSERT INTO Budget (mese_anno, importo_budget, id_categoria)
VALUES ('2026-02', 300.00, 1);