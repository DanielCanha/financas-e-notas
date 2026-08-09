def moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def progresso_meta(valor_atual: float, valor_alvo: float) -> float:
    if valor_alvo <= 0:
        return 0.0
    return max(0.0, valor_atual / valor_alvo * 100)


def tendencia_preco(atual: float | None, anterior: float | None) -> tuple[str, str]:
    if atual is None or anterior is None:
        return "—", "neutra"
    diferenca = atual - anterior
    if diferenca < 0:
        return f"↓ {moeda(abs(diferenca))}", "queda"
    if diferenca > 0:
        return f"↑ {moeda(diferenca)}", "alta"
    return "→ sem alteração", "neutra"
