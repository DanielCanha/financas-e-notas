import sqlite3

from db import BancoDados, RepositorioFinancas


def test_banco_existente_recebe_coluna_origem(tmp_path):
    caminho = tmp_path / "legado.db"
    with sqlite3.connect(caminho) as con:
        con.execute(
            "CREATE TABLE receitas (id INTEGER PRIMARY KEY AUTOINCREMENT, mes_ano TEXT NOT NULL, valor REAL NOT NULL)"
        )
        con.execute("INSERT INTO receitas(mes_ano, valor) VALUES ('2026-08', 1000)")

    banco = BancoDados(caminho)
    receita = RepositorioFinancas(banco).listar_receitas("2026-08")[0]
    assert receita["origem"] == "Não informado"
