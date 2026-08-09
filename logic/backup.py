import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


TABELAS_EXPORTAVEIS = (
    "receitas", "gastos", "metas", "notas", "itens_desejo", "historico_preco"
)


def criar_backup(caminho_banco: Path, pasta_destino: Path, manter: int = 20) -> Path | None:
    if not caminho_banco.exists():
        return None
    pasta_destino.mkdir(parents=True, exist_ok=True)
    destino = pasta_destino / f"financas_notas_{datetime.now():%Y-%m-%d_%H-%M-%S}.db"
    shutil.copy2(caminho_banco, destino)
    backups = sorted(pasta_destino.glob("financas_notas_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for antigo in backups[manter:]:
        antigo.unlink(missing_ok=True)
    return destino


def exportar_csvs(caminho_banco: Path, pasta_destino: Path) -> list[Path]:
    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivos: list[Path] = []
    with sqlite3.connect(caminho_banco) as con:
        con.row_factory = sqlite3.Row
        for tabela in TABELAS_EXPORTAVEIS:
            linhas = con.execute(f"SELECT * FROM {tabela}").fetchall()
            colunas = [item[1] for item in con.execute(f"PRAGMA table_info({tabela})")]
            destino = pasta_destino / f"{tabela}.csv"
            with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.writer(arquivo)
                escritor.writerow(colunas)
                escritor.writerows([[linha[coluna] for coluna in colunas] for linha in linhas])
            arquivos.append(destino)
    return arquivos
