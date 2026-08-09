from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFormLayout, QLineEdit, QVBoxLayout,
)


def campo_moeda() -> QDoubleSpinBox:
    campo = QDoubleSpinBox()
    campo.setRange(0, 999_999_999)
    campo.setDecimals(2)
    campo.setPrefix("R$ ")
    campo.setSingleStep(10)
    return campo


class DialogoGasto(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar gasto")
        self.descricao = QLineEdit()
        self.categoria = QComboBox()
        self.categoria.setEditable(True)
        self.categoria.addItems(["Moradia", "Alimentação", "Transporte", "Saúde", "Lazer", "Educação", "Outros"])
        self.valor = campo_moeda()
        self.data = QDateEdit(QDate.currentDate())
        self.data.setCalendarPopup(True)
        self.data.setDisplayFormat("dd/MM/yyyy")
        self.recorrente = QCheckBox("Gasto recorrente")
        formulario = QFormLayout()
        formulario.addRow("Descrição", self.descricao)
        formulario.addRow("Categoria", self.categoria)
        formulario.addRow("Valor", self.valor)
        formulario.addRow("Data", self.data)
        formulario.addRow("", self.recorrente)
        botoes = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self._validar)
        botoes.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botoes)

    def _validar(self):
        if self.descricao.text().strip() and self.categoria.currentText().strip() and self.valor.value() > 0:
            self.accept()

    def dados(self):
        return (
            self.descricao.text().strip(), self.categoria.currentText().strip(), self.valor.value(),
            self.data.date().toString("yyyy-MM-dd"), self.recorrente.isChecked(),
        )


class DialogoValor(QDialog):
    def __init__(self, titulo: str, rotulo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.valor = campo_moeda()
        formulario = QFormLayout()
        formulario.addRow(rotulo, self.valor)
        botoes = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botoes.accepted.connect(lambda: self.accept() if self.valor.value() > 0 else None)
        botoes.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botoes)


class DialogoReceita(QDialog):
    def __init__(self, titulo: str = "Adicionar receita", parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.origem = QLineEdit()
        self.origem.setPlaceholderText("Ex.: Salário, FGTS, trabalho extra")
        self.valor = campo_moeda()
        formulario = QFormLayout()
        formulario.addRow("Origem", self.origem)
        formulario.addRow("Valor recebido", self.valor)
        botoes = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self._validar)
        botoes.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botoes)

    def _validar(self):
        if self.origem.text().strip() and self.valor.value() > 0:
            self.accept()


class DialogoMeta(DialogoValor):
    def __init__(self, parent=None):
        super().__init__("Definir meta", "Valor limite", parent)
        self.categoria = QComboBox()
        self.categoria.setEditable(True)
        self.categoria.addItems(["Meta geral", "Moradia", "Alimentação", "Transporte", "Saúde", "Lazer", "Educação", "Outros"])
        formulario = self.layout().itemAt(0).layout()
        formulario.insertRow(0, "Categoria", self.categoria)

    def categoria_escolhida(self):
        texto = self.categoria.currentText().strip()
        return None if texto == "Meta geral" else texto


class DialogoDesejo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo item desejado")
        self.nome = QLineEdit()
        self.preco = campo_moeda()
        self.link = QLineEdit()
        self.link.setPlaceholderText("https://… (opcional)")
        formulario = QFormLayout()
        formulario.addRow("Produto", self.nome)
        formulario.addRow("Preço inicial", self.preco)
        formulario.addRow("Link", self.link)
        botoes = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botoes.accepted.connect(lambda: self.accept() if self.nome.text().strip() and self.preco.value() > 0 else None)
        botoes.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botoes)
