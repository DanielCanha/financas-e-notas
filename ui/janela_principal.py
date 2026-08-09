from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QPushButton, QTabWidget

from app_paths import caminho_banco, pasta_backups
from logic.backup import criar_backup, exportar_csvs
from .estilos import ESTILO_GLOBAL
from .financas import TelaFinancas
from .notas import TelaNotas
from .painel import TelaPainel


class JanelaPrincipal(QMainWindow):
    def __init__(self, repositorio_financas, repositorio_notas, repositorio_desejos):
        super().__init__()
        self.setWindowTitle("Finanças & Notas")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)
        self.setStyleSheet(ESTILO_GLOBAL)

        self.abas = QTabWidget()
        self.abas.setDocumentMode(True)
        self.painel = TelaPainel(repositorio_financas, repositorio_notas)
        self.notas = TelaNotas(repositorio_notas)
        self.financas = TelaFinancas(repositorio_financas, repositorio_desejos)
        self.abas.addTab(self.painel, "Painel")
        self.abas.addTab(self.notas, "Notas")
        self.abas.addTab(self.financas, "Finanças")
        self.setCentralWidget(self.abas)

        exportar = QPushButton("Exportar dados")
        exportar.setProperty("secondary", True)
        exportar.clicked.connect(self.exportar_dados)
        self.statusBar().addPermanentWidget(exportar)
        self.statusBar().showMessage(f"Dados salvos em {caminho_banco()}")

        self.abas.currentChanged.connect(self.atualizar_aba)
        self.notas.dados_alterados.connect(self.painel.atualizar)
        self.financas.dados_alterados.connect(self.painel.atualizar)
        self.painel.atualizar()

    def atualizar_aba(self, indice: int):
        widget = self.abas.widget(indice)
        if hasattr(widget, "atualizar"):
            widget.atualizar()

    def exportar_dados(self):
        pasta = QFileDialog.getExistingDirectory(self, "Escolha a pasta para exportar")
        if not pasta:
            return
        destino = Path(pasta) / f"financas_notas_exportacao_{datetime.now():%Y-%m-%d_%H-%M-%S}"
        try:
            arquivos = exportar_csvs(caminho_banco(), destino)
            QMessageBox.information(self, "Exportação concluída", f"{len(arquivos)} arquivos CSV criados em:\n{destino}")
        except OSError as erro:
            QMessageBox.critical(self, "Falha na exportação", str(erro))

    def closeEvent(self, evento):
        self.notas.salvar_atual()
        try:
            criar_backup(caminho_banco(), pasta_backups())
        except OSError as erro:
            resposta = QMessageBox.warning(
                self, "Backup não criado", f"Não foi possível criar o backup:\n{erro}\n\nDeseja sair mesmo assim?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
            )
            if resposta == QMessageBox.No:
                evento.ignore()
                return
        evento.accept()
