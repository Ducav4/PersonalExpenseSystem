import sqlite3

# Nome del file database
NOME_DB = "spese.db"

# Funzione per creare le tabelle all'inizio
def setup_iniziale():
    connessione = sqlite3.connect(NOME_DB)
    puntatore = connessione.cursor() 
    
    # Creazione Tabella Categorie
    # ID autoincrementante e nome unico per evitare duplicati
    puntatore.execute("""
        CREATE TABLE IF NOT EXISTS Categorie (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_categoria TEXT UNIQUE NOT NULL
        )
    """)
    
    # Creazione Tabella Spese
    # Il vincolo CHECK serve per impedire importi negativi o zero
    puntatore.execute("""
        CREATE TABLE IF NOT EXISTS Spese (
            id_spesa INTEGER PRIMARY KEY AUTOINCREMENT,
            data_spesa TEXT NOT NULL,
            importo REAL NOT NULL CHECK(importo > 0),
            descrizione TEXT,
            id_categoria INTEGER NOT NULL,
            FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria)
        )
    """)
    
    # Creazione Tabella Budget
    # UNIQUE su mese e categoria così non ho due budget per la stessa cosa
    puntatore.execute("""
        CREATE TABLE IF NOT EXISTS Budget (
            id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
            mese_anno TEXT NOT NULL,
            importo_budget REAL NOT NULL CHECK(importo_budget > 0),
            id_categoria INTEGER NOT NULL,
            UNIQUE(mese_anno, id_categoria),
            FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria)
        )
    """)
    
    connessione.commit()
    connessione.close()

# MODULO 1: Gestione Categorie
def agg_categoria():
    print("\n--- NUOVA CATEGORIA ---")
    nome_cat = input("Nome della categoria: ")
    
    # Controllo che non sia vuoto
    if nome_cat == "":
        print("Errore: devi scrivere un nome!")
        return

    connessione = sqlite3.connect(NOME_DB)
    puntatore = connessione.cursor()
    
    # Prima controllo se c'è già
    puntatore.execute("SELECT * FROM Categorie WHERE nome_categoria = ?", (nome_cat,))
    trovato = puntatore.fetchone()
    
    if trovato == None:
        puntatore.execute("INSERT INTO Categorie (nome_categoria) VALUES (?)", (nome_cat,))
        connessione.commit()
        print("Fatto! Categoria aggiunta.")
    else:
        print("Attenzione: questa categoria esiste già.")
        
    connessione.close()

# MODULO 2: Inserimento Spesa
def agg_spesa():
    print("\n--- NUOVA SPESA ---")
    data = input("Data (formato YYYY-MM-DD): ")
    
    # Provo a convertire il numero
    try:
        valore = float(input("Importo spesa: "))
    except:
        print("Errore: devi inserire un numero valido (usa il punto per i decimali).")
        return

    # Controllo che l'importo non sia negativo
    if valore <= 0:
        print("Errore: l'importo deve essere positivo!")
        return

    nome_c = input("Categoria: ")
    desc = input("Descrizione (facoltativa): ")
    
    connessione = sqlite3.connect(NOME_DB)
    puntatore = connessione.cursor()
    
    # Trovo l'ID della categoria dal nome
    puntatore.execute("SELECT id_categoria FROM Categorie WHERE nome_categoria = ?", (nome_c,))
    ris = puntatore.fetchone()
    
    if ris == None:
        print("Errore: Categoria non trovata. Creala prima nel menu 1.")
    else:
        id_c = ris[0] # Prendo il primo elemento della lista (l'ID)
        
        # Inserisco la spesa
        puntatore.execute("INSERT INTO Spese (data_spesa, importo, descrizione, id_categoria) VALUES (?, ?, ?, ?)", (data, valore, desc, id_c))
        connessione.commit()
        print("Spesa salvata correttamente.")
        
    connessione.close()

# MODULO 3: Budget Mensile
def agg_budget():
    print("\n--- BUDGET MENSILE ---")
    mese = input("Mese (es. 2026-02): ")
    cat = input("Categoria: ")
    
    try:
        bud_val = float(input("Budget massimo: "))
    except:
        print("Numero non valido.")
        return
        
    if bud_val <= 0:
        print("Il budget deve essere maggiore di 0.")
        return

    connessione = sqlite3.connect(NOME_DB)
    puntatore = connessione.cursor()
    
    # Controllo se la categoria esiste
    puntatore.execute("SELECT id_categoria FROM Categorie WHERE nome_categoria = ?", (cat,))
    ris = puntatore.fetchone()
    
    if ris == None:
        print("Categoria inesistente.")
    else:
        id_c = ris[0]
        
        # Controllo se c'è già un budget per quel mese
        puntatore.execute("SELECT * FROM Budget WHERE mese_anno = ? AND id_categoria = ?", (mese, id_c))
        check = puntatore.fetchone()
        
        if check == None:
            # Se non c'è, lo creo (INSERT)
            puntatore.execute("INSERT INTO Budget (mese_anno, id_categoria, importo_budget) VALUES (?, ?, ?)", (mese, id_c, bud_val))
            print("Budget creato.")
        else:
            # Se c'è, lo aggiorno (UPDATE)
            puntatore.execute("UPDATE Budget SET importo_budget = ? WHERE mese_anno = ? AND id_categoria = ?", (bud_val, mese, id_c))
            print("Budget aggiornato.")
        
        connessione.commit()
    connessione.close()

# MODULO 4: Visualizzazione Report
def mostra_report():
    connessione = sqlite3.connect(NOME_DB)
    puntatore = connessione.cursor()

    while True:
        print("\n--- REPORT ---")
        print("1. Totali per Categoria")
        print("2. Verifica Budget (Mese)")
        print("3. Lista di tutte le spese")
        print("4. Indietro")
        
        scelta = input("Cosa vuoi vedere? ")
        
        if scelta == "1":
            print("CATEGORIA \t TOTALE")
            print("-" * 30)
            # Query 
            puntatore.execute("""
                SELECT Categorie.nome_categoria, SUM(Spese.importo) 
                FROM Spese, Categorie 
                WHERE Spese.id_categoria = Categorie.id_categoria 
                GROUP BY Categorie.nome_categoria
            """)
            for riga in puntatore.fetchall():
                print(riga[0], "\t\t", riga[1])
                
        elif scelta == "2":
            mese_input = input("Inserisci il mese (YYYY-MM): ")
            
            # Prendo i budget impostati per quel mese
            puntatore.execute("""
                SELECT Categorie.nome_categoria, Budget.importo_budget, Budget.id_categoria 
                FROM Budget, Categorie 
                WHERE Budget.id_categoria = Categorie.id_categoria AND Budget.mese_anno = ?
            """, (mese_input,))
            budgets = puntatore.fetchall()
            
            print(f"--- Situazione {mese_input} ---")
            for b in budgets:
                nome = b[0]
                limite = b[1]
                id_cat_b = b[2]
                
                # Calcolo quanto ho speso davvero per quella categoria
                puntatore.execute("SELECT SUM(importo) FROM Spese WHERE id_categoria = ? AND data_spesa LIKE ?", (id_cat_b, mese_input + "%"))
                somma = puntatore.fetchone()[0]
                
                if somma == None:
                    somma = 0.0
                
                stato = "OK"
                if somma > limite:
                    stato = "SUPERAMENTO BUDGET!!"
                
                print(f"{nome} -> Budget: {limite} | Speso: {somma} -> {stato}")
        
        elif scelta == "3":
            print("DATA \t\t IMPORTO \t CATEGORIA")
            puntatore.execute("""
                SELECT Spese.data_spesa, Spese.importo, Categorie.nome_categoria
                FROM Spese, Categorie 
                WHERE Spese.id_categoria = Categorie.id_categoria 
                ORDER BY Spese.data_spesa DESC
            """)
            for x in puntatore.fetchall():
                print(f"{x[0]} \t {x[1]} \t {x[2]}")
                
        elif scelta == "4":
            break
        else:
            print("Scelta non valida.")
            
    connessione.close()

# PROGRAMMA PRINCIPALE
print("--- GESTIONE SPESE PERSONALI ---")
setup_iniziale() # Crea il db se serve

while True:
    print("\n1. Gestisci Categorie")
    print("2. Aggiungi Spesa")
    print("3. Gestisci Budget")
    print("4. Report")
    print("5. Esci")
    
    tasto = input("Scegli un numero: ")
    
    if tasto == "1":
        agg_categoria()
    elif tasto == "2":
        agg_spesa()
    elif tasto == "3":
        agg_budget()
    elif tasto == "4":
        mostra_report()
    elif tasto == "5":
        print("Ciao!")
        break
    else:
        print("Scelta non valida. Riprovare.")