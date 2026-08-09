from datetime import date

from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QScrollArea, QVBoxLayout, QWidget,
)

from logic.calculos import moeda, progresso_meta


def card() -> tuple[QFrame, QVBoxLayout]:
    quadro = QFrame()
    quadro.setObjectName("card")
    layout = QVBoxLayout(quadro)
    layout.setContentsMargins(18, 16, 18, 16)
    return quadro, layout


class TelaPainel(QWidget):
    def __init__(self, repositorio_financas, repositorio_notas):
        super().__init__()
        self.financas = repositorio_financas
        self.notas = repositorio_notas
        self.mes_ano = date.today().strftime("%Y-%m")

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(24, 22, 24, 24)
        titulo = QLabel("Visão geral")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)

        grade = QGridLayout()
        grade.setSpacing(16)
        raiz.addLayout(grade)

        quadro_grafico, layout_grafico = card()
        self.resumo = QLabel()
        self.resumo.setWordWrap(True)
        self.grafico = QChartView()
        self.grafico.setRenderHint(QPainter.Antialiasing)
        self.grafico.setMinimumHeight(290)
        layout_grafico.addWidget(QLabel("Resumo financeiro"))
        layout_grafico.addWidget(self.grafico)
        layout_grafico.addWidget(self.resumo)
        grade.addWidget(quadro_grafico, 0, 0, 2, 1)

        quadro_meta, layout_meta = card()
        layout_meta.addWidget(QLabel("Meta do mês"))
        self.meta_texto = QLabel()
        self.meta_texto.setObjectName("valorGrande")
        self.meta_detalhe = QLabel()
        self.meta_detalhe.setProperty("muted", True)
        self.barra_meta = QProgressBar()
        self.barra_meta.setTextVisible(False)
        layout_meta.addWidget(self.meta_texto)
        layout_meta.addWidget(self.meta_detalhe)
        layout_meta.addWidget(self.barra_meta)
        grade.addWidget(quadro_meta, 0, 1)

        quadro_programados, layout_programados = card()
        layout_programados.addWidget(QLabel("Gastos programados"))
        self.lista_programados = QListWidget()
        self.lista_programados.setMinimumHeight(170)
        layout_programados.addWidget(self.lista_programados)
        grade.addWidget(quadro_programados, 1, 1)

        quadro_notas, layout_notas = card()
        layout_notas.addWidget(QLabel("Notas fixadas"))
        self.area_notas = QScrollArea()
        self.area_notas.setWidgetResizable(True)
        self.area_notas.setFrameShape(QFrame.NoFrame)
        self.conteudo_notas = QWidget()
        self.layout_notas = QHBoxLayout(self.conteudo_notas)
        self.layout_notas.setAlignment(Qt.AlignLeft)
        self.area_notas.setWidget(self.conteudo_notas)
        layout_notas.addWidget(self.area_notas)
        grade.addWidget(quadro_notas, 2, 0, 1, 2)
        grade.setColumnStretch(0, 3)
        grade.setColumnStretch(1, 2)
        raiz.addStretch()

    def atualizar(self):
        recebido = self.financas.total_receita(self.mes_ano)
        gasto = self.financas.total_gasto(self.mes_ano, somente_feitos=True)
        sobra = recebido - gasto
        serie = QPieSeries()
        valores = [("Recebido", recebido), ("Gasto", gasto), ("Sobra", max(0, sobra))]
        cores = ["#22c55e", "#ef4444", "#3b82f6"]
        if not any(valor > 0 for _, valor in valores):
            valores = [("Sem dados", 1)]
            cores = ["#cbd5e1"]
        for (nome, valor), cor in zip(valores, cores):
            fatia = serie.append(f"{nome}: {moeda(valor)}", valor)
            fatia.setBrush(QColor(cor))
            fatia.setLabelVisible(valor > 0)
        grafico = QChart()
        grafico.addSeries(serie)
        grafico.legend().setVisible(True)
        grafico.setBackgroundVisible(False)
        grafico.setMargins(QMargins(0, 0, 0, 0))
        self.grafico.setChart(grafico)
        self.resumo.setText(f"Recebido: {moeda(recebido)}   •   Gasto: {moeda(gasto)}   •   Sobra: {moeda(sobra)}")

        meta = self.financas.meta_relevante(self.mes_ano)
        if meta:
            percentual = progresso_meta(meta["valor_atual"], meta["valor_alvo"])
            self.meta_texto.setText(f"{percentual:.0f}%")
            nome = meta["categoria"] or "Geral"
            self.meta_detalhe.setText(f"{nome}: {moeda(meta['valor_atual'])} de {moeda(meta['valor_alvo'])}")
            self.barra_meta.setValue(min(100, round(percentual)))
        else:
            self.meta_texto.setText("Sem meta")
            self.meta_detalhe.setText("Defina uma meta no controle financeiro")
            self.barra_meta.setValue(0)

        self.lista_programados.clear()
        for gasto_programado in self.financas.gastos_programados(self.mes_ano):
            texto = f"{gasto_programado['data'][8:10]}/{gasto_programado['data'][5:7]}  {gasto_programado['descricao']}  ·  {moeda(gasto_programado['valor'])}"
            self.lista_programados.addItem(QListWidgetItem(texto))
        if not self.lista_programados.count():
            self.lista_programados.addItem("Nenhum gasto programado neste mês")

        while self.layout_notas.count():
            item = self.layout_notas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        notas = self.notas.listar(somente_fixadas=True)
        if not notas:
            vazio = QLabel("Nenhuma nota fixada")
            vazio.setProperty("muted", True)
            self.layout_notas.addWidget(vazio)
        for nota in notas:
            quadro, layout = card()
            quadro.setFixedWidth(230)
            titulo = QLabel(nota["titulo"])
            titulo.setObjectName("subtitulo")
            previa = QLabel((nota["conteudo"] or "Sem conteúdo")[:160])
            previa.setWordWrap(True)
            previa.setProperty("muted", True)
            layout.addWidget(titulo)
            layout.addWidget(previa)
            self.layout_notas.addWidget(quadro)
