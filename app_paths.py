from pathlib import Path

from platformdirs import user_data_path


APP_NAME = "FinancasENotas"
APP_AUTHOR = "Daniel"


def pasta_dados() -> Path:
    caminho = user_data_path(APP_NAME, APP_AUTHOR, ensure_exists=True)
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def caminho_banco() -> Path:
    return pasta_dados() / "financas_notas.db"


def pasta_backups() -> Path:
    caminho = pasta_dados() / "backups"
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho
