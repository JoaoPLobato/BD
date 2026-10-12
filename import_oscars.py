import pandas as pd
import sqlite3

# Conectar à base de dados
conn = sqlite3.connect('oscares.db')
# Criar cursor
cur = conn.cursor()
cur.row_factory = sqlite3.Row

#Criar as tabelas
cur.executescript("""

    CREATE TABLE IF NOT EXISTS Cerimonia (
    Num_Cerimonia INTEGER PRIMARY KEY NOT NULL,
    Ano TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Categoria (
    Categoria_Canonica TEXT PRIMARY KEY NOT NULL,
    Classe TEXT NOT NULL,
    Cat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Filme (
    IDFilme TEXT PRIMARY KEY,
    Titulo TEXT
);

CREATE TABLE IF NOT EXISTS Nomeado (
    IDNomeado TEXT PRIMARY KEY NOT NULL,
    Nome TEXT
);

CREATE TABLE IF NOT EXISTS Nomeacao (
    IDNomeacao TEXT PRIMARY KEY NOT NULL ,
    Num_Cerimonia INTEGER NOT NULL,
    Categoria_Canonica TEXT NOT NULL,
    Vencedor BOOLEAN,
    Detalhes TEXT,
    Notas TEXT,
    Citacao TEXT,
    IDFilme TEXT,
    FOREIGN KEY (Num_Cerimonia) REFERENCES Cerimonia(Num_Cerimonia),
    FOREIGN KEY (Categoria_Canonica) REFERENCES Categoria(Categoria_Canonica),
    FOREIGN KEY (Vencedor) REFERENCES Nomeado(IDNomeado),
    FOREIGN KEY (IDFilme) REFERENCES Filme(IDFilme)
);


CREATE TABLE IF NOT EXISTS NomeiaN (
    IDNomeado TEXT ,
    IDNomeacao TEXT ,
    PRIMARY KEY (IDNomeado,IDNomeacao),
    FOREIGN KEY (IDNomeado) REFERENCES Nomeado(IDNomeado),
    FOREIGN KEY (IDNomeacao) REFERENCES Nomeacao(IDNomeacao)
);

""")

conn.commit()

#Leitura do ficheiro excel e a sua conversão numa dataframe: df
df = pd.read_excel("oscars.xlsx")
df.columns = [c.strip() for c in df.columns]

########################### Povoar tabela Cerimonia

years=df['Year'].unique()
B=df['Ceremony'].unique()
B1=[int(c) for c in B]

data=list(zip(B1, years))

sql = ("INSERT OR IGNORE INTO Cerimonia(Num_Cerimonia, Ano) VALUES (?,?)")
cur.executemany(sql, data)
conn.commit()

########################### Povoar tabela Filme

films = df[['FilmId', 'Film']].drop_duplicates()
films = films.dropna(subset=['FilmId'])  # só filmes com ID válido

data2 = [(row.FilmId, row.Film) for _, row in films.iterrows()]

sql2 = "INSERT OR IGNORE INTO Filme(IDFilme, Titulo) VALUES (?,?)"
cur.executemany(sql2, data2)

conn.commit()


########################### Povoar tabela Categoria

cat = df[['Class', 'CanonicalCategory', 'Category']].drop_duplicates()

data3 = [(row.CanonicalCategory, row.Category, row.Class) for _, row in cat.iterrows()]

sql3 = "INSERT OR IGNORE INTO Categoria(Categoria_Canonica, Cat, Classe) VALUES (?,?,?)"
cur.executemany(sql3, data3)

conn.commit()


########################################## Separar ids de nomeados e os seus nomes que estão na mesma nomeação


df_nomeados = df[['NomId', 'NomineeIds', 'Nominees']].dropna(subset=['NomineeIds'])

rows = []

for _, row in df_nomeados.iterrows():
    nomination_id = str(row['NomId'])
    # Separa os múltiplos IDs e nomes
    ids = [x.strip() for x in str(row['NomineeIds']).split(',')]
    names = [x.strip() for x in str(row['Nominees']).split(',')]

    if len(ids) != len(names):
        continue

    # Liga cada ID com o nome correspondente
    for i in range(len(ids)):
        rows.append((ids[i], names[i], nomination_id))  # IDNomeado, Nome, IDNomeacao

# Cria DataFrame limpo com o formato necessário
df_clean = pd.DataFrame(rows, columns=['IDNomeado', 'Nome', 'IDNomeacao'])

########################### Povoar tabela Nomeado

# Remover duplicados de Nomeado
nomeados = df_clean[['IDNomeado', 'Nome']].drop_duplicates()

# Inserir na base de dados
data_nomeados = list(nomeados.itertuples(index=False, name=None))
sql_nomeados = "INSERT OR IGNORE INTO Nomeado(IDNomeado, Nome) VALUES (?, ?)"
cur.executemany(sql_nomeados, data_nomeados)
conn.commit()

########################### Povoar tabela NomeiaN


# Remover duplicados na relação Nomeado ↔ Nomeacao
nomeian = df_clean[['IDNomeado', 'IDNomeacao']].drop_duplicates()

data_nomeian = list(nomeian.itertuples(index=False, name=None))
sql_nomeian = "INSERT OR IGNORE INTO NomeiaN(IDNomeado, IDNomeacao) VALUES (?, ?)"
cur.executemany(sql_nomeian, data_nomeian)
conn.commit()

########################### Povoar tabela Nomeacao

noms = df[['NomId', 'Ceremony', 'CanonicalCategory', 'Winner', 'Detail', 'Note', 'Citation','FilmId']].drop_duplicates()

# Remove linhas onde não há ID da nomeação (pois é PK não null)
noms = noms.dropna(subset=['NomId'])

# Converter Ids em string
noms['NomId'] = noms['NomId'].astype(str)
noms['Ceremony'] = noms['Ceremony'].astype(int)
noms['CanonicalCategory'] = noms['CanonicalCategory'].astype(str)
noms['FilmId'] = noms['FilmId'].astype(str)

data_noms = list(noms.itertuples(index=False, name=None))

sql_noms = """
INSERT OR IGNORE INTO Nomeacao(
    IDNomeacao, Num_Cerimonia, Categoria_Canonica, Vencedor, Detalhes, Notas, Citacao, IDFilme
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

cur.executemany(sql_noms, data_noms)
conn.commit()