import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes_ano TEXT NOT NULL,
    origem TEXT NOT NULL DEFAULT 'Não informado',
    valor REAL NOT NULL CHECK (valor >= 0)
);

CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor REAL NOT NULL CHECK (valor >= 0),
    data TEXT NOT NULL,
    recorrente INTEGER DEFAULT 0 CHECK (recorrente IN (0, 1))
);

CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes_ano TEXT NOT NULL,
    categoria TEXT,
    valor_alvo REAL NOT NULL CHECK (valor_alvo >= 0)
);

CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    fixada_no_painel INTEGER DEFAULT 0 CHECK (fixada_no_painel IN (0, 1)),
    criada_em TEXT NOT NULL,
    atualizada_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS itens_desejo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_produto TEXT NOT NULL,
    link TEXT,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS historico_preco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES itens_desejo(id) ON DELETE CASCADE,
    preco REAL NOT NULL CHECK (preco >= 0),
    verificado_em TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_receitas_mes ON receitas(mes_ano);
CREATE INDEX IF NOT EXISTS idx_gastos_data ON gastos(data);
CREATE INDEX IF NOT EXISTS idx_metas_mes ON metas(mes_ano);
CREATE INDEX IF NOT EXISTS idx_historico_item ON historico_preco(item_id, verificado_em DESC, id DESC);
"""


class BancoDados:
    def __init__(self, caminho: str | Path):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.inicializar()

    def conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def inicializar(self) -> None:
        with self.conectar() as conexao:
            conexao.executescript(SCHEMA)
            colunas_receitas = {linha[1] for linha in conexao.execute("PRAGMA table_info(receitas)")}
            if "origem" not in colunas_receitas:
                conexao.execute(
                    "ALTER TABLE receitas ADD COLUMN origem TEXT NOT NULL DEFAULT 'Não informado'"
                )
