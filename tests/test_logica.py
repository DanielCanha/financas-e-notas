from logic.calculos import moeda, progresso_meta, tendencia_preco


def test_formatacao_monetaria():
    assert moeda(1234.5) == "R$ 1.234,50"
    assert moeda(-12.3) == "R$ -12,30"


def test_progresso_meta():
    assert progresso_meta(250, 1000) == 25
    assert progresso_meta(10, 0) == 0


def test_tendencia_preco():
    assert tendencia_preco(90, 100)[1] == "queda"
    assert tendencia_preco(110, 100)[1] == "alta"
    assert tendencia_preco(100, None) == ("—", "neutra")
