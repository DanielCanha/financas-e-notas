from datetime import date

from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDate, QDateTime, Qt, QUrl, Signal
from PySide6.QtGui import QBrush, QColor, QCursor, QDesktopServices, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
    QMessageBox, QPushButton, QStackedWidget, QTableWidget, QTableWidgetItem,
    QTabWidget, QToolTip, QVBoxLayout, QWidget,
)

from logic.calculos import moeda, progresso_meta, tendencia_preco
from .dialogos import DialogoDesejo, DialogoGasto, DialogoMeta, DialogoReceita, DialogoValor


MESES = ("Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro")


class DialogoReceitas(QDialog):
    def __init__(self, repositorio, mes_ano: str, titulo_mes: str, parent=None):
        super().__init__(parent)
        self.repositorio = repositorio
        self.mes_ano = mes_ano
        self.setWindowTitle(f"Receitas de {titulo_mes}")
        self.resize(620, 420)
        layout = QVBoxLayout(self)
        topo = QHBoxLayout()
        titulo = QLabel(f"Receitas de {titulo_mes}")
        titulo.setObjectName("subtitulo")
        adicionar = QPushButton("+ Adicionar receita")
        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(adicionar)
        layout.addLayout(topo)
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Origem", "Valor", "Editar", "Excluir"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.tabela)
        rodape = QHBoxLayout()
        self.total = QLabel()
        self.total.setObjectName("valorGrande")
        fechar = QPushButton("Fechar")
        fechar.setProperty("secondary", True)
        rodape.addWidget(self.total)
        rodape.addStretch()
        rodape.addWidget(fechar)
        layout.addLayout(rodape)
        adicionar.clicked.connect(self.adicionar)
        fechar.clicked.connect(self.accept)
        self.atualizar()

    def atualizar(self):
        receitas = self.repositorio.listar_receitas(self.mes_ano)
        self.tabela.setRowCount(len(receitas))
        for linha, receita in enumerate(receitas):
            self.tabela.setItem(linha, 0, QTableWidgetItem(receita["origem"]))
            valor = QTableWidgetItem(moeda(receita["valor"]))
            valor.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(linha, 1, valor)
            editar = QPushButton("Editar")
            editar.setProperty("secondary", True)
            editar.clicked.connect(lambda _, r=receita: self.editar(r))
            self.tabela.setCellWidget(linha, 2, editar)
            excluir = QPushButton("Excluir")
            excluir.setProperty("danger", True)
            excluir.clicked.connect(lambda _, receita_id=receita["id"]: self.excluir(receita_id))
            self.tabela.setCellWidget(linha, 3, excluir)
        self.total.setText(f"Total recebido: {moeda(sum(r['valor'] for r in receitas))}")

    def adicionar(self):
        dialogo = DialogoReceita("Adicionar receita", self)
        if dialogo.exec() == QDialog.Accepted:
            self.repositorio.adicionar_receita(
                self.mes_ano, dialogo.valor.value(), dialogo.origem.text()
            )
            self.atualizar()

    def editar(self, receita):
        dialogo = DialogoReceita("Editar receita", self)
        dialogo.valor.setValue(receita["valor"])
        dialogo.origem.setText(receita["origem"])
        if dialogo.exec() == QDialog.Accepted:
            self.repositorio.atualizar_receita(
                receita["id"], dialogo.valor.value(), dialogo.origem.text()
            )
            self.atualizar()

    def excluir(self, receita_id: int):
        if QMessageBox.question(self, "Excluir receita", "Deseja excluir esta receita?") == QMessageBox.Yes:
            self.repositorio.excluir_receita(receita_id)
            self.atualizar()


class DialogoHistoricoPrecos(QDialog):
    def __init__(self, repositorio, item_id: int, nome_produto: str, parent=None):
        super().__init__(parent)
        self.repositorio = repositorio
        self.item_id = item_id
        self.nome_produto = nome_produto
        self.setWindowTitle(f"Histórico de preços — {nome_produto}")
        self.resize(760, 520)
        layout = QVBoxLayout(self)
        titulo = QLabel(nome_produto)
        titulo.setObjectName("subtitulo")
        layout.addWidget(titulo)
        self.abas = QTabWidget()
        self.tabela = QTableWidget(0, 4)
        self.tabela.setHorizontalHeaderLabels(["Data da verificação", "Preço", "Variação", ""])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grafico = QChartView()
        self.grafico.setRenderHint(QPainter.Antialiasing)
        self.abas.addTab(self.tabela, "Tabela")
        self.abas.addTab(self.grafico, "Gráfico")
        layout.addWidget(self.abas)
        fechar = QPushButton("Fechar")
        fechar.setProperty("secondary", True)
        fechar.clicked.connect(self.accept)
        layout.addWidget(fechar, alignment=Qt.AlignRight)
        self.atualizar()

    def atualizar(self):
        historico = self.repositorio.historico_precos(self.item_id)
        self.tabela.setRowCount(len(historico))
        for linha, registro in enumerate(historico):
            data_iso = registro["verificado_em"]
            data_br = f"{data_iso[8:10]}/{data_iso[5:7]}/{data_iso[:4]}"
            if "T" in data_iso:
                data_br += f" {data_iso[11:16]}"
            anterior = historico[linha + 1]["preco"] if linha + 1 < len(historico) else None
            variacao, tipo = tendencia_preco(registro["preco"], anterior)
            self.tabela.setItem(linha, 0, QTableWidgetItem(data_br))
            self.tabela.setItem(linha, 1, QTableWidgetItem(moeda(registro["preco"])))
            item_variacao = QTableWidgetItem(variacao if anterior is not None else "Preço inicial")
            cor = {"queda": "#15803d", "alta": "#dc2626"}.get(tipo, "#64748b")
            item_variacao.setForeground(QBrush(QColor(cor)))
            self.tabela.setItem(linha, 2, item_variacao)
            excluir = QPushButton("Excluir")
            excluir.setProperty("danger", True)
            excluir.setEnabled(len(historico) > 1)
            excluir.setToolTip(
                "É necessário manter ao menos um preço" if len(historico) <= 1 else "Excluir este registro"
            )
            excluir.clicked.connect(
                lambda _, historico_id=registro["id"]: self.excluir_registro(historico_id)
            )
            self.tabela.setCellWidget(linha, 3, excluir)
        self._atualizar_grafico(historico)

    def excluir_registro(self, historico_id: int):
        if QMessageBox.question(
            self, "Excluir preço", "Deseja excluir este registro do histórico?"
        ) != QMessageBox.Yes:
            return
        if not self.repositorio.excluir_preco(historico_id, self.item_id):
            QMessageBox.warning(self, "Preço obrigatório", "O produto precisa manter ao menos um preço.")
            return
        self.atualizar()

    def _atualizar_grafico(self, historico):
        serie = QLineSeries()
        serie.setName(self.nome_produto)
        serie.setPointsVisible(True)
        serie.setMarkerSize(9)
        serie.setPen(QPen(QColor("#66c0f4"), 3))
        detalhes = {}
        ocorrencias_por_data = {}
        anterior = None
        valores_x = []
        valores_y = []
        for registro in reversed(historico):
            data_iso = registro["verificado_em"]
            apenas_data = data_iso[:10]
            chave_ocorrencia = data_iso if "T" in data_iso else apenas_data
            ocorrencia = ocorrencias_por_data.get(chave_ocorrencia, 0)
            ocorrencias_por_data[chave_ocorrencia] = ocorrencia + 1
            momento = QDateTime.fromString(data_iso, Qt.ISODate)
            if not momento.isValid():
                momento = QDateTime.fromString(apenas_data, "yyyy-MM-dd")
            x = momento.toMSecsSinceEpoch() + ocorrencia * 60_000
            preco = registro["preco"]
            serie.append(x, preco)
            diferenca = None if anterior is None else preco - anterior
            percentual = None if anterior in (None, 0) else diferenca / anterior * 100
            ordem_legada = ocorrencia + 1 if "T" not in data_iso else 1
            detalhes[x] = (data_iso, preco, diferenca, percentual, ordem_legada)
            valores_x.append(x)
            valores_y.append(preco)
            anterior = preco
        serie.hovered.connect(lambda ponto, ativo: self._mostrar_detalhes(ponto, ativo, detalhes))

        grafico = QChart()
        grafico.setTheme(QChart.ChartThemeLight)
        grafico.setBackgroundVisible(False)
        grafico.setPlotAreaBackgroundVisible(True)
        grafico.setPlotAreaBackgroundBrush(QBrush(QColor("#ffffff")))
        grafico.legend().setVisible(False)
        grafico.addSeries(serie)
        eixo_data = QDateTimeAxis()
        intervalo = max(valores_x) - min(valores_x) if valores_x else 0
        um_dia = 86_400_000
        if intervalo < um_dia:
            eixo_data.setFormat("dd/MM HH:mm")
            eixo_data.setTickCount(min(5, max(2, len(historico))))
        elif intervalo < 90 * um_dia:
            eixo_data.setFormat("dd/MM")
            eixo_data.setTickCount(min(7, max(2, len(historico))))
        else:
            eixo_data.setFormat("MMM/yy")
            eixo_data.setTickCount(min(7, max(2, len(historico))))
        eixo_data.setTitleText("Período")
        eixo_data.setGridLineColor(QColor("#e2e8f0"))
        eixo_data.setLabelsColor(QColor("#64748b"))
        eixo_valor = QValueAxis()
        eixo_valor.setLabelFormat("R$ %.0f")
        eixo_valor.setTitleText("Preço")
        eixo_valor.setGridLineColor(QColor("#e2e8f0"))
        eixo_valor.setLabelsColor(QColor("#64748b"))
        grafico.addAxis(eixo_data, Qt.AlignBottom)
        grafico.addAxis(eixo_valor, Qt.AlignLeft)
        serie.attachAxis(eixo_data)
        serie.attachAxis(eixo_valor)
        if valores_x:
            margem_x = max(5 * 60_000, intervalo * 0.08)
            if len(valores_x) == 1:
                margem_x = 30 * um_dia
            eixo_data.setRange(
                QDateTime.fromMSecsSinceEpoch(round(min(valores_x) - margem_x)),
                QDateTime.fromMSecsSinceEpoch(round(max(valores_x) + margem_x)),
            )
            minimo_y, maximo_y = min(valores_y), max(valores_y)
            margem_y = max(1.0, (maximo_y - minimo_y) * 0.15, maximo_y * 0.03)
            eixo_valor.setRange(max(0, minimo_y - margem_y), maximo_y + margem_y)
        self.grafico.setChart(grafico)

    def _mostrar_detalhes(self, ponto, ativo: bool, detalhes):
        if not ativo:
            QToolTip.hideText()
            return
        if not detalhes:
            QToolTip.hideText()
            return
        chave_mais_proxima = min(detalhes, key=lambda chave: abs(chave - ponto.x()))
        data_iso, preco, diferenca, percentual, ordem = detalhes[chave_mais_proxima]
        data_br = f"{data_iso[8:10]}/{data_iso[5:7]}/{data_iso[:4]}"
        if "T" in data_iso:
            data_br += f" às {data_iso[11:16]}"
        elif ordem > 1:
            data_br += f" · {ordem}ª verificação do dia"
        linhas = [f"<b>{data_br}</b>", f"Preço: {moeda(preco)}"]
        if diferenca is not None:
            sinal = "+" if diferenca > 0 else ""
            linhas.append(f"Variação: {sinal}{moeda(diferenca)} ({sinal}{percentual:.1f}%)")
        else:
            linhas.append("Primeiro preço registrado")
        QToolTip.showText(QCursor.pos(), "<br>".join(linhas), self.grafico)


class TelaFinancas(QWidget):
    dados_alterados = Signal()

    def __init__(self, repositorio_financas, repositorio_desejos):
        super().__init__()
        self.financas = repositorio_financas
        self.desejos = repositorio_desejos
        hoje = date.today()
        self.ano, self.mes = hoje.year, hoje.month
        self.modo_exclusao = False

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(24, 22, 24, 24)
        topo = QHBoxLayout()
        titulo = QLabel("Controle financeiro")
        titulo.setObjectName("titulo")
        self.botao_gastos = QPushButton("Gastos")
        self.botao_desejos = QPushButton("Lista de desejos")
        self.botao_desejos.setProperty("secondary", True)
        topo.addWidget(titulo)
        topo.addStretch()
        topo.addWidget(self.botao_gastos)
        topo.addWidget(self.botao_desejos)
        raiz.addLayout(topo)

        self.pilhas = QStackedWidget()
        self.pagina_gastos = self._criar_pagina_gastos()
        self.pagina_desejos = self._criar_pagina_desejos()
        self.pilhas.addWidget(self.pagina_gastos)
        self.pilhas.addWidget(self.pagina_desejos)
        raiz.addWidget(self.pilhas, 1)

        self.botao_gastos.clicked.connect(lambda: self.alternar_modo(0))
        self.botao_desejos.clicked.connect(lambda: self.alternar_modo(1))
        self.atualizar()

    @property
    def mes_ano(self):
        return f"{self.ano:04d}-{self.mes:02d}"

    def _criar_pagina_gastos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 16, 0, 0)
        navegacao = QHBoxLayout()
        anterior = QPushButton("‹")
        anterior.setProperty("secondary", True)
        proximo = QPushButton("›")
        proximo.setProperty("secondary", True)
        self.rotulo_mes = QLabel()
        self.rotulo_mes.setObjectName("subtitulo")
        self.rotulo_meta = QLabel()
        self.rotulo_meta.setProperty("muted", True)
        botao_receita = QPushButton("Gerenciar receitas")
        botao_receita.setProperty("secondary", True)
        botao_meta = QPushButton("Definir meta")
        botao_meta.setProperty("secondary", True)
        botao_adicionar = QPushButton("+ Novo gasto")
        navegacao.addWidget(anterior)
        navegacao.addWidget(self.rotulo_mes)
        navegacao.addWidget(proximo)
        navegacao.addSpacing(20)
        navegacao.addWidget(self.rotulo_meta)
        navegacao.addStretch()
        navegacao.addWidget(botao_receita)
        navegacao.addWidget(botao_meta)
        navegacao.addWidget(botao_adicionar)
        layout.addLayout(navegacao)

        resumo = QHBoxLayout()
        self.rotulo_receitas = QLabel()
        self.rotulo_receitas.setObjectName("valorGrande")
        self.rotulo_gastos_resumo = QLabel()
        self.rotulo_gastos_resumo.setObjectName("valorGrande")
        self.rotulo_saldo = QLabel()
        self.rotulo_saldo.setObjectName("valorGrande")
        resumo.addWidget(self.rotulo_receitas)
        resumo.addStretch()
        resumo.addWidget(self.rotulo_gastos_resumo)
        resumo.addStretch()
        resumo.addWidget(self.rotulo_saldo)
        layout.addLayout(resumo)

        self.tabela_gastos = QTableWidget(0, 6)
        self.tabela_gastos.setHorizontalHeaderLabels(["Data", "Descrição", "Categoria", "Status", "Valor", ""])
        self.tabela_gastos.setAlternatingRowColors(True)
        self.tabela_gastos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela_gastos.verticalHeader().setVisible(False)
        cabecalho = self.tabela_gastos.horizontalHeader()
        cabecalho.setSectionResizeMode(1, QHeaderView.Stretch)
        cabecalho.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.tabela_gastos, 1)
        self.rotulo_total = QLabel()
        self.rotulo_total.setObjectName("valorGrande")
        self.rotulo_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.rotulo_total)

        anterior.clicked.connect(lambda: self.mudar_mes(-1))
        proximo.clicked.connect(lambda: self.mudar_mes(1))
        botao_adicionar.clicked.connect(self.adicionar_gasto)
        botao_receita.clicked.connect(self.gerenciar_receitas)
        botao_meta.clicked.connect(self.definir_meta)
        return pagina

    def _criar_pagina_desejos(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 16, 0, 0)
        topo = QHBoxLayout()
        self.total_desejos = QLabel()
        self.total_desejos.setObjectName("valorGrande")
        self.botao_excluir_desejos = QPushButton("Excluir")
        self.botao_excluir_desejos.setProperty("danger", True)
        botao_adicionar = QPushButton("+ Novo item")
        topo.addWidget(QLabel("Total da lista:"))
        topo.addWidget(self.total_desejos)
        topo.addStretch()
        topo.addWidget(self.botao_excluir_desejos)
        topo.addWidget(botao_adicionar)
        layout.addLayout(topo)

        self.tabela_desejos = QTableWidget(0, 7)
        self.tabela_desejos.setHorizontalHeaderLabels(["", "Produto", "Preço atual", "Variação", "Produto", "Histórico", "Preço"])
        self.tabela_desejos.verticalHeader().setVisible(False)
        self.tabela_desejos.setAlternatingRowColors(True)
        self.tabela_desejos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.tabela_desejos, 1)
        botao_adicionar.clicked.connect(self.adicionar_desejo)
        self.botao_excluir_desejos.clicked.connect(self.acao_excluir_desejos)
        return pagina

    def alternar_modo(self, indice: int):
        self.pilhas.setCurrentIndex(indice)
        self.botao_gastos.setProperty("secondary", indice != 0)
        self.botao_desejos.setProperty("secondary", indice == 0)
        for botao in (self.botao_gastos, self.botao_desejos):
            botao.style().unpolish(botao)
            botao.style().polish(botao)
        self.atualizar()

    def mudar_mes(self, delta: int):
        total = self.ano * 12 + self.mes - 1 + delta
        self.ano, indice = divmod(total, 12)
        self.mes = indice + 1
        self.atualizar_gastos()

    def atualizar(self):
        self.atualizar_gastos()
        self.atualizar_desejos()

    def atualizar_gastos(self):
        self.rotulo_mes.setText(f"{MESES[self.mes - 1]} de {self.ano}")
        gastos = self.financas.listar_gastos(self.mes_ano)
        self.tabela_gastos.setRowCount(len(gastos))
        hoje = date.today().isoformat()
        for linha, gasto in enumerate(gastos):
            data_br = f"{gasto['data'][8:10]}/{gasto['data'][5:7]}/{gasto['data'][:4]}"
            valores = [data_br, gasto["descricao"], gasto["categoria"], "Feito" if gasto["data"] <= hoje else "Agendado", moeda(gasto["valor"])]
            for coluna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                if coluna == 4:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabela_gastos.setItem(linha, coluna, item)
            botao = QPushButton("Remover")
            botao.setProperty("danger", True)
            botao.clicked.connect(lambda _, gasto_id=gasto["id"]: self.excluir_gasto(gasto_id))
            self.tabela_gastos.setCellWidget(linha, 5, botao)
        total = sum(gasto["valor"] for gasto in gastos)
        self.rotulo_total.setText(f"Total do mês: {moeda(total)}")
        total_receitas = self.financas.total_receita(self.mes_ano)
        self.rotulo_receitas.setText(f"Receitas\n{moeda(total_receitas)}")
        self.rotulo_gastos_resumo.setText(f"Gastos\n{moeda(total)}")
        self.rotulo_saldo.setText(f"Saldo\n{moeda(total_receitas - total)}")
        meta = self.financas.meta_relevante(self.mes_ano)
        if meta:
            categoria = meta["categoria"] or "geral"
            percentual = progresso_meta(meta["valor_atual"], meta["valor_alvo"])
            self.rotulo_meta.setText(f"Meta {categoria}: {percentual:.0f}% de {moeda(meta['valor_alvo'])}")
        else:
            self.rotulo_meta.setText("Nenhuma meta definida")

    def adicionar_gasto(self):
        dialogo = DialogoGasto(self)
        dialogo.data.setDate(QDate(self.ano, self.mes, min(date.today().day, QDate(self.ano, self.mes, 1).daysInMonth())))
        if dialogo.exec() == QDialog.Accepted:
            self.financas.adicionar_gasto(*dialogo.dados())
            self.atualizar_gastos()
            self.dados_alterados.emit()

    def excluir_gasto(self, gasto_id: int):
        if QMessageBox.question(self, "Remover gasto", "Deseja remover este gasto?") == QMessageBox.Yes:
            self.financas.excluir_gasto(gasto_id)
            self.atualizar_gastos()
            self.dados_alterados.emit()

    def gerenciar_receitas(self):
        titulo_mes = f"{MESES[self.mes - 1]} de {self.ano}"
        DialogoReceitas(self.financas, self.mes_ano, titulo_mes, self).exec()
        self.atualizar_gastos()
        self.dados_alterados.emit()

    def definir_meta(self):
        dialogo = DialogoMeta(self)
        if dialogo.exec() == QDialog.Accepted:
            self.financas.definir_meta(self.mes_ano, dialogo.valor.value(), dialogo.categoria_escolhida())
            self.atualizar_gastos()
            self.dados_alterados.emit()

    def atualizar_desejos(self):
        itens = self.desejos.listar()
        self.tabela_desejos.setRowCount(len(itens))
        self.total_desejos.setText(moeda(sum(item["preco_atual"] or 0 for item in itens)))
        for linha, item in enumerate(itens):
            selecao = QCheckBox()
            selecao.setProperty("item_id", item["id"])
            selecao.setVisible(self.modo_exclusao)
            self.tabela_desejos.setCellWidget(linha, 0, selecao)
            tendencia, tipo = tendencia_preco(item["preco_atual"], item["preco_anterior"])
            self.tabela_desejos.setItem(linha, 1, QTableWidgetItem(item["nome_produto"]))
            self.tabela_desejos.setItem(linha, 2, QTableWidgetItem(moeda(item["preco_atual"] or 0)))
            variacao = QTableWidgetItem(tendencia)
            cor = {"queda": "#15803d", "alta": "#dc2626"}.get(tipo, "#64748b")
            variacao.setForeground(QBrush(QColor(cor)))
            self.tabela_desejos.setItem(linha, 3, variacao)
            if item["link"]:
                link = QPushButton("Ver produto")
                link.setProperty("secondary", True)
                link.clicked.connect(lambda _, url=item["link"]: QDesktopServices.openUrl(QUrl(url)))
                self.tabela_desejos.setCellWidget(linha, 4, link)
            historico = QPushButton("Ver histórico")
            historico.setProperty("secondary", True)
            historico.clicked.connect(
                lambda _, item_id=item["id"], nome=item["nome_produto"]: self.ver_historico(item_id, nome)
            )
            self.tabela_desejos.setCellWidget(linha, 5, historico)
            atualizar = QPushButton("Atualizar preço")
            atualizar.setProperty("secondary", True)
            atualizar.clicked.connect(lambda _, item_id=item["id"]: self.atualizar_preco(item_id))
            self.tabela_desejos.setCellWidget(linha, 6, atualizar)
        self.botao_excluir_desejos.setText("Excluir marcados" if self.modo_exclusao else "Excluir")

    def adicionar_desejo(self):
        dialogo = DialogoDesejo(self)
        if dialogo.exec() == QDialog.Accepted:
            self.desejos.adicionar(dialogo.nome.text(), dialogo.preco.value(), dialogo.link.text())
            self.atualizar_desejos()
            self.dados_alterados.emit()

    def atualizar_preco(self, item_id: int):
        dialogo = DialogoValor("Atualizar preço", "Novo preço", self)
        if dialogo.exec() == QDialog.Accepted:
            self.desejos.atualizar_preco(item_id, dialogo.valor.value())
            self.atualizar_desejos()
            self.dados_alterados.emit()

    def ver_historico(self, item_id: int, nome_produto: str):
        DialogoHistoricoPrecos(self.desejos, item_id, nome_produto, self).exec()
        self.atualizar_desejos()
        self.dados_alterados.emit()

    def acao_excluir_desejos(self):
        if not self.modo_exclusao:
            self.modo_exclusao = True
            self.atualizar_desejos()
            return
        ids = []
        for linha in range(self.tabela_desejos.rowCount()):
            checkbox = self.tabela_desejos.cellWidget(linha, 0)
            if checkbox and checkbox.isChecked():
                ids.append(checkbox.property("item_id"))
        if ids and QMessageBox.question(self, "Excluir itens", f"Excluir {len(ids)} item(ns) selecionado(s)?") == QMessageBox.Yes:
            self.desejos.excluir_varios(ids)
            self.dados_alterados.emit()
        self.modo_exclusao = False
        self.atualizar_desejos()
