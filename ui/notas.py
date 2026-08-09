from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)


class TelaNotas(QWidget):
    dados_alterados = Signal()

    def __init__(self, repositorio):
        super().__init__()
        self.repositorio = repositorio
        self.nota_id: int | None = None
        self.carregando = False
        self.timer_salvar = QTimer(self)
        self.timer_salvar.setSingleShot(True)
        self.timer_salvar.setInterval(500)
        self.timer_salvar.timeout.connect(self.salvar_atual)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(24, 22, 24, 24)
        topo = QHBoxLayout()
        titulo = QLabel("Bloco de notas")
        titulo.setObjectName("titulo")
        self.botao_nova = QPushButton("+ Nova nota")
        self.botao_excluir = QPushButton("Excluir")
        self.botao_excluir.setProperty("danger", True)
        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(self.botao_excluir)
        topo.addWidget(self.botao_nova)
        raiz.addLayout(topo)

        corpo = QHBoxLayout()
        corpo.setSpacing(14)
        self.lista = QListWidget()
        self.lista.setFixedWidth(310)
        corpo.addWidget(self.lista)
        editor = QVBoxLayout()
        self.titulo = QLineEdit()
        self.titulo.setPlaceholderText("Título")
        self.titulo.setStyleSheet("font-size: 20px; font-weight: 650; padding: 10px;")
        self.conteudo = QTextEdit()
        self.conteudo.setPlaceholderText("Escreva sua nota…")
        self.fixada = QCheckBox("Fixar no painel principal")
        editor.addWidget(self.titulo)
        editor.addWidget(self.conteudo)
        editor.addWidget(self.fixada)
        corpo.addLayout(editor, 1)
        raiz.addLayout(corpo, 1)

        self.botao_nova.clicked.connect(self.criar_nota)
        self.botao_excluir.clicked.connect(self.excluir_atual)
        self.lista.currentItemChanged.connect(self.selecionar)
        self.titulo.textChanged.connect(self.agendar_salvamento)
        self.conteudo.textChanged.connect(self.agendar_salvamento)
        self.fixada.toggled.connect(self.agendar_salvamento)
        self.atualizar()

    def atualizar(self, selecionar_id: int | None = None):
        atual = selecionar_id if selecionar_id is not None else self.nota_id
        self.lista.blockSignals(True)
        self.lista.clear()
        alvo = None
        for nota in self.repositorio.listar():
            previa = " ".join((nota["conteudo"] or "").split())[:65]
            pino = "📌 " if nota["fixada_no_painel"] else ""
            item = QListWidgetItem(f"{pino}{nota['titulo']}\n{previa}")
            item.setData(Qt.UserRole, nota)
            item.setSizeHint(item.sizeHint().expandedTo(item.sizeHint() + QSize(0, 28)))
            self.lista.addItem(item)
            if nota["id"] == atual:
                alvo = item
        self.lista.blockSignals(False)
        if alvo:
            self.lista.setCurrentItem(alvo)
            self.selecionar(alvo, None)
        elif self.lista.count():
            self.lista.setCurrentRow(0)
        else:
            self._limpar_editor()

    def selecionar(self, item, anterior):
        if not item:
            return
        nota = item.data(Qt.UserRole)
        self.carregando = True
        self.nota_id = nota["id"]
        self.titulo.setText(nota["titulo"])
        self.conteudo.setPlainText(nota["conteudo"] or "")
        self.fixada.setChecked(bool(nota["fixada_no_painel"]))
        self.carregando = False

    def agendar_salvamento(self, *_):
        if not self.carregando and self.nota_id is not None:
            self.timer_salvar.start()

    def salvar_atual(self):
        if self.nota_id is None:
            return
        nota_id = self.nota_id
        self.repositorio.atualizar(nota_id, self.titulo.text(), self.conteudo.toPlainText(), self.fixada.isChecked())
        self.dados_alterados.emit()
        self.atualizar(nota_id)

    def criar_nota(self):
        self.salvar_atual()
        novo_id = self.repositorio.criar()
        self.nota_id = novo_id
        self.atualizar(novo_id)
        self.titulo.setFocus()
        self.titulo.selectAll()
        self.dados_alterados.emit()

    def excluir_atual(self):
        if self.nota_id is None:
            return
        resposta = QMessageBox.question(self, "Excluir nota", "Deseja excluir esta nota?")
        if resposta == QMessageBox.Yes:
            self.repositorio.excluir(self.nota_id)
            self.nota_id = None
            self.atualizar()
            self.dados_alterados.emit()

    def _limpar_editor(self):
        self.carregando = True
        self.nota_id = None
        self.titulo.clear()
        self.conteudo.clear()
        self.fixada.setChecked(False)
        self.carregando = False
