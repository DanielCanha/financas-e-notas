# Finanças & Notas

Aplicativo desktop pessoal para organizar receitas, gastos, metas, notas e uma lista de desejos com histórico de preços. Os dados ficam em um banco SQLite na pasta de dados do usuário, fora da instalação do programa.

Consulte [DOCUMENTACAO_FUNCIONAL.md](DOCUMENTACAO_FUNCIONAL.md) para conhecer o funcionamento completo, arquitetura, modelo de dados, regras, limitações e recomendações de evolução.

## Executar no Linux

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python main.py
```

O caminho exato do banco é exibido na barra inferior do aplicativo. Ao fechar, uma cópia é criada em `backups/`; somente as 20 mais recentes são mantidas. Para ter uma cópia na nuvem, configure seu serviço (Google Drive, OneDrive ou Dropbox) para sincronizar essa pasta.

## Recursos

- Painel mensal com gráfico, meta, gastos programados e notas fixadas.
- Notas com salvamento automático, fixação e exclusão.
- Gastos, receitas identificadas por origem e metas navegáveis por mês, com resumo de saldo.
- Lista de desejos com histórico editável, registros com data e hora, gráfico de linhas com escala adaptativa e hover, links e exclusão múltipla.
- Exportação de cada tabela do banco para CSV.

## Testes e build

```bash
.venv/bin/python -m pytest
.venv/bin/pyinstaller --clean financas_notas.spec
```

O build deve ser feito separadamente em cada sistema operacional. O arquivo `.spec` inclui os plugins do Qt para evitar o erro do plugin `xcb` no Linux.
# financas-e-notas
# financas-e-notas
# financas-e-notas
# financas-e-notas
