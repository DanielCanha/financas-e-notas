from db import BancoDados, RepositorioDesejos, RepositorioFinancas, RepositorioNotas


def test_crud_principal(tmp_path):
    banco = BancoDados(tmp_path / "teste.db")
    financas = RepositorioFinancas(banco)
    notas = RepositorioNotas(banco)
    desejos = RepositorioDesejos(banco)

    receita_id = financas.adicionar_receita("2026-08", 5000)
    financas.adicionar_gasto("Mercado", "Alimentação", 300, "2026-08-02", False)
    financas.definir_meta("2026-08", 1000)
    assert financas.total_receita("2026-08") == 5000
    assert financas.total_gasto("2026-08") == 300
    assert financas.meta_relevante("2026-08")["valor_atual"] == 300
    financas.atualizar_receita(receita_id, 5500, "Salário")
    assert financas.total_receita("2026-08") == 5500
    assert financas.listar_receitas("2026-08")[0]["origem"] == "Salário"
    financas.excluir_receita(receita_id)
    assert financas.listar_receitas("2026-08") == []

    nota_id = notas.criar("Lembrete", "Conteúdo", True)
    notas.atualizar(nota_id, "Novo título", "Novo conteúdo", False)
    assert notas.listar()[0]["titulo"] == "Novo título"

    item_id = desejos.adicionar("Notebook", 5000, "https://example.com")
    desejos.atualizar_preco(item_id, 4500)
    item = desejos.listar()[0]
    assert item["preco_atual"] == 4500
    assert item["preco_anterior"] == 5000
    assert [registro["preco"] for registro in desejos.historico_precos(item_id)] == [4500, 5000]
    registro_errado = desejos.historico_precos(item_id)[0]["id"]
    assert desejos.excluir_preco(registro_errado, item_id) is True
    unico_registro = desejos.historico_precos(item_id)[0]["id"]
    assert desejos.excluir_preco(unico_registro, item_id) is False
    desejos.excluir_varios([item_id])
    assert desejos.listar() == []
