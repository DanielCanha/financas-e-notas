from datetime import date, datetime
from typing import Any

from .database import BancoDados


class RepositorioFinancas:
    def __init__(self, banco: BancoDados):
        self.banco = banco

    def listar_gastos(self, mes_ano: str) -> list[dict[str, Any]]:
        with self.banco.conectar() as con:
            linhas = con.execute(
                "SELECT * FROM gastos WHERE substr(data, 1, 7) = ? ORDER BY data, id", (mes_ano,)
            ).fetchall()
        return [dict(linha) for linha in linhas]

    def adicionar_gasto(self, descricao: str, categoria: str, valor: float, data_iso: str, recorrente: bool) -> int:
        with self.banco.conectar() as con:
            cursor = con.execute(
                "INSERT INTO gastos(descricao, categoria, valor, data, recorrente) VALUES (?, ?, ?, ?, ?)",
                (descricao.strip(), categoria.strip(), valor, data_iso, int(recorrente)),
            )
            return int(cursor.lastrowid)

    def excluir_gasto(self, gasto_id: int) -> None:
        with self.banco.conectar() as con:
            con.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))

    def total_gasto(self, mes_ano: str, somente_feitos: bool = False) -> float:
        sql = "SELECT COALESCE(SUM(valor), 0) FROM gastos WHERE substr(data, 1, 7) = ?"
        params: list[Any] = [mes_ano]
        if somente_feitos:
            sql += " AND data <= ?"
            params.append(date.today().isoformat())
        with self.banco.conectar() as con:
            return float(con.execute(sql, params).fetchone()[0])

    def gastos_programados(self, mes_ano: str) -> list[dict[str, Any]]:
        with self.banco.conectar() as con:
            linhas = con.execute(
                "SELECT * FROM gastos WHERE substr(data, 1, 7) = ? AND data > ? ORDER BY data",
                (mes_ano, date.today().isoformat()),
            ).fetchall()
        return [dict(linha) for linha in linhas]

    def listar_receitas(self, mes_ano: str) -> list[dict[str, Any]]:
        with self.banco.conectar() as con:
            linhas = con.execute("SELECT * FROM receitas WHERE mes_ano = ? ORDER BY id", (mes_ano,)).fetchall()
        return [dict(linha) for linha in linhas]

    def adicionar_receita(self, mes_ano: str, valor: float, origem: str = "Não informado") -> int:
        with self.banco.conectar() as con:
            cursor = con.execute(
                "INSERT INTO receitas(mes_ano, origem, valor) VALUES (?, ?, ?)",
                (mes_ano, origem.strip() or "Não informado", valor),
            )
            return int(cursor.lastrowid)

    def atualizar_receita(self, receita_id: int, valor: float, origem: str) -> None:
        with self.banco.conectar() as con:
            con.execute(
                "UPDATE receitas SET valor = ?, origem = ? WHERE id = ?",
                (valor, origem.strip() or "Não informado", receita_id),
            )

    def excluir_receita(self, receita_id: int) -> None:
        with self.banco.conectar() as con:
            con.execute("DELETE FROM receitas WHERE id = ?", (receita_id,))

    def total_receita(self, mes_ano: str) -> float:
        with self.banco.conectar() as con:
            return float(con.execute(
                "SELECT COALESCE(SUM(valor), 0) FROM receitas WHERE mes_ano = ?", (mes_ano,)
            ).fetchone()[0])

    def definir_meta(self, mes_ano: str, valor: float, categoria: str | None = None) -> None:
        with self.banco.conectar() as con:
            if categoria:
                con.execute("DELETE FROM metas WHERE mes_ano = ? AND categoria = ?", (mes_ano, categoria))
            else:
                con.execute("DELETE FROM metas WHERE mes_ano = ? AND categoria IS NULL", (mes_ano,))
            con.execute(
                "INSERT INTO metas(mes_ano, categoria, valor_alvo) VALUES (?, ?, ?)",
                (mes_ano, categoria, valor),
            )

    def meta_relevante(self, mes_ano: str) -> dict[str, Any] | None:
        with self.banco.conectar() as con:
            linha = con.execute(
                """
                SELECT m.*,
                       CASE WHEN m.categoria IS NULL THEN
                           (SELECT COALESCE(SUM(valor), 0) FROM gastos WHERE substr(data, 1, 7) = m.mes_ano)
                       ELSE
                           (SELECT COALESCE(SUM(valor), 0) FROM gastos
                            WHERE substr(data, 1, 7) = m.mes_ano AND categoria = m.categoria)
                       END AS valor_atual
                FROM metas m WHERE m.mes_ano = ?
                ORDER BY CASE WHEN m.categoria IS NOT NULL THEN 0 ELSE 1 END, valor_atual DESC, m.id
                LIMIT 1
                """,
                (mes_ano,),
            ).fetchone()
        return dict(linha) if linha else None


class RepositorioNotas:
    def __init__(self, banco: BancoDados):
        self.banco = banco

    def listar(self, somente_fixadas: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM notas"
        if somente_fixadas:
            sql += " WHERE fixada_no_painel = 1"
        sql += " ORDER BY fixada_no_painel DESC, atualizada_em DESC, id DESC"
        with self.banco.conectar() as con:
            linhas = con.execute(sql).fetchall()
        return [dict(linha) for linha in linhas]

    def criar(self, titulo: str = "Nova nota", conteudo: str = "", fixada: bool = False) -> int:
        agora = datetime.now().isoformat(timespec="seconds")
        with self.banco.conectar() as con:
            cursor = con.execute(
                "INSERT INTO notas(titulo, conteudo, fixada_no_painel, criada_em, atualizada_em) VALUES (?, ?, ?, ?, ?)",
                (titulo, conteudo, int(fixada), agora, agora),
            )
            return int(cursor.lastrowid)

    def atualizar(self, nota_id: int, titulo: str, conteudo: str, fixada: bool) -> None:
        with self.banco.conectar() as con:
            con.execute(
                "UPDATE notas SET titulo = ?, conteudo = ?, fixada_no_painel = ?, atualizada_em = ? WHERE id = ?",
                (titulo.strip() or "Sem título", conteudo, int(fixada), datetime.now().isoformat(timespec="seconds"), nota_id),
            )

    def excluir(self, nota_id: int) -> None:
        with self.banco.conectar() as con:
            con.execute("DELETE FROM notas WHERE id = ?", (nota_id,))


class RepositorioDesejos:
    def __init__(self, banco: BancoDados):
        self.banco = banco

    def listar(self) -> list[dict[str, Any]]:
        with self.banco.conectar() as con:
            linhas = con.execute(
                """
                SELECT i.*,
                    (SELECT preco FROM historico_preco h WHERE h.item_id = i.id
                     ORDER BY verificado_em DESC, id DESC LIMIT 1) AS preco_atual,
                    (SELECT preco FROM historico_preco h WHERE h.item_id = i.id
                     ORDER BY verificado_em DESC, id DESC LIMIT 1 OFFSET 1) AS preco_anterior
                FROM itens_desejo i ORDER BY criado_em DESC, id DESC
                """
            ).fetchall()
        return [dict(linha) for linha in linhas]

    def adicionar(self, nome: str, preco: float, link: str | None = None) -> int:
        agora = datetime.now().isoformat(timespec="seconds")
        with self.banco.conectar() as con:
            cursor = con.execute(
                "INSERT INTO itens_desejo(nome_produto, link, criado_em) VALUES (?, ?, ?)",
                (nome.strip(), link.strip() if link and link.strip() else None, agora),
            )
            item_id = int(cursor.lastrowid)
            con.execute(
                "INSERT INTO historico_preco(item_id, preco, verificado_em) VALUES (?, ?, ?)",
                (item_id, preco, datetime.now().isoformat(timespec="seconds")),
            )
            return item_id

    def atualizar_preco(self, item_id: int, preco: float) -> None:
        with self.banco.conectar() as con:
            con.execute(
                "INSERT INTO historico_preco(item_id, preco, verificado_em) VALUES (?, ?, ?)",
                (item_id, preco, datetime.now().isoformat(timespec="seconds")),
            )

    def historico_precos(self, item_id: int) -> list[dict[str, Any]]:
        with self.banco.conectar() as con:
            linhas = con.execute(
                """
                SELECT id, item_id, preco, verificado_em
                FROM historico_preco
                WHERE item_id = ?
                ORDER BY verificado_em DESC, id DESC
                """,
                (item_id,),
            ).fetchall()
        return [dict(linha) for linha in linhas]

    def excluir_preco(self, historico_id: int, item_id: int) -> bool:
        """Exclui um preço somente quando outro registro mantém o item utilizável."""
        with self.banco.conectar() as con:
            quantidade = con.execute(
                "SELECT COUNT(*) FROM historico_preco WHERE item_id = ?", (item_id,)
            ).fetchone()[0]
            if quantidade <= 1:
                return False
            con.execute(
                "DELETE FROM historico_preco WHERE id = ? AND item_id = ?", (historico_id, item_id)
            )
            return True

    def excluir_varios(self, ids: list[int]) -> None:
        if not ids:
            return
        marcadores = ",".join("?" for _ in ids)
        with self.banco.conectar() as con:
            con.execute(f"DELETE FROM itens_desejo WHERE id IN ({marcadores})", ids)
