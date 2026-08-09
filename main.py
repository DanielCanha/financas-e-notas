import sys

from PySide6.QtWidgets import QApplication

from app_paths import caminho_banco
from db import BancoDados, RepositorioDesejos, RepositorioFinancas, RepositorioNotas
from ui import JanelaPrincipal


def criar_aplicacao() -> tuple[QApplication, JanelaPrincipal]:
    aplicacao = QApplication.instance() or QApplication(sys.argv)
    aplicacao.setApplicationName("Finanças & Notas")
    aplicacao.setOrganizationName("Daniel")
    banco = BancoDados(caminho_banco())
    janela = JanelaPrincipal(
        RepositorioFinancas(banco),
        RepositorioNotas(banco),
        RepositorioDesejos(banco),
    )
    return aplicacao, janela


def main() -> int:
    aplicacao, janela = criar_aplicacao()
    janela.show()
    return aplicacao.exec()


if __name__ == "__main__":
    raise SystemExit(main())
