# Documentação funcional e técnica — Finanças & Notas

Atualizada em 09/08/2026.

## 1. Visão geral

Finanças & Notas é um aplicativo desktop pessoal e local para acompanhar receitas, gastos, metas financeiras, notas e produtos desejados. O programa foi pensado para um único usuário, sem login e sem dependência de serviços externos.

Os dados são persistidos em SQLite fora da pasta de instalação. Isso permite substituir ou atualizar o executável sem apagar o banco. A interface é construída com PySide6 e o executável Linux é gerado com PyInstaller.

### Funcionalidades entregues

- Painel com resumo financeiro do mês atual.
- Cadastro e acompanhamento de receitas por origem.
- Cadastro e acompanhamento de gastos por mês.
- Metas gerais ou por categoria.
- Bloco de notas com salvamento automático e fixação no painel.
- Lista de desejos com preço atual, tendência e link do produto.
- Histórico completo de preços em tabela e gráfico de linhas interativo.
- Exclusão de registros incorretos do histórico, mantendo ao menos um preço.
- Backup automático do banco ao fechar.
- Exportação de todas as tabelas para CSV.
- Migração automática para bancos criados antes da inclusão da origem da receita.

## 2. Tecnologias

| Componente | Tecnologia | Finalidade |
|---|---|---|
| Linguagem | Python 3.12+ | Implementação do aplicativo |
| Interface | PySide6 / Qt Widgets | Janelas, formulários, tabelas e navegação |
| Gráficos | PySide6.QtCharts | Pizza do painel e linha do histórico de preços |
| Banco | SQLite via `sqlite3` | Persistência local sem servidor |
| Caminhos | `platformdirs` | Pasta de dados adequada ao sistema operacional |
| Testes | pytest | Testes da lógica, repositórios e migração |
| Empacotamento | PyInstaller | Geração do executável nativo |

## 3. Organização do projeto

```text
Finanças & Notas
├── main.py                         ponto de entrada
├── app_paths.py                    caminhos do banco e dos backups
├── db/
│   ├── database.py                 conexão, esquema e migrações
│   └── repositorios.py             operações de leitura e gravação
├── logic/
│   ├── calculos.py                 moeda, metas e tendência de preços
│   └── backup.py                   backup e exportação CSV
├── ui/
│   ├── janela_principal.py         janela, abas, exportação e fechamento
│   ├── painel.py                   painel principal
│   ├── notas.py                    bloco de notas
│   ├── financas.py                 gastos, receitas, desejos e gráficos
│   ├── dialogos.py                 formulários reutilizáveis
│   └── estilos.py                  estilo global da interface
├── tests/                          testes automatizados
├── financas_notas.spec             configuração do PyInstaller
├── requirements.txt                dependências de execução
└── requirements-dev.txt            dependências de desenvolvimento
```

### Separação em camadas

O projeto segue três camadas principais:

1. `ui/`: apresenta informações e recebe ações do usuário.
2. `logic/`: executa cálculos e tarefas que não dependem da interface.
3. `db/`: concentra o esquema e as consultas SQLite.

A janela não executa SQL diretamente. Ela chama os repositórios, que abrem conexões curtas com o banco e devolvem dicionários. Essa separação facilita testes e alterações futuras na interface.

## 4. Inicialização do aplicativo

Ao executar `main.py`, o programa realiza esta sequência:

1. Cria ou reutiliza uma instância de `QApplication`.
2. Resolve a pasta de dados com `platformdirs`.
3. Cria a pasta, caso ainda não exista.
4. Abre ou cria `financas_notas.db`.
5. Cria as tabelas e índices ausentes.
6. Executa a migração da coluna `origem` em bancos antigos.
7. Cria os repositórios de finanças, notas e desejos.
8. Constrói a janela com as abas Painel, Notas e Finanças.
9. Atualiza o painel e inicia o loop de eventos do Qt.

O caminho real do banco é mostrado na barra inferior da janela.

## 5. Funcionamento das telas

## 5.1. Painel

O painel sempre representa o mês atual do sistema.

### Resumo financeiro

O gráfico de pizza e o texto inferior utilizam:

- Recebido: soma de todas as receitas do mês atual.
- Gasto: soma dos gastos do mês cuja data seja menor ou igual à data de hoje.
- Sobra: recebido menos gasto.

Uma sobra negativa aparece corretamente no resumo textual. Para o gráfico de pizza, valores negativos não podem formar uma fatia; por isso, a fatia de sobra usa zero quando o saldo é negativo.

### Meta do mês

O painel procura uma meta do mês. Quando existem metas por categoria, prioriza a categoria com maior valor atualmente gasto. Caso não exista meta de categoria, utiliza a meta geral.

O percentual é calculado assim:

```text
percentual = valor gasto / valor-alvo × 100
```

A barra visual é limitada a 100%, mas o texto pode informar percentuais superiores quando a meta foi ultrapassada.

### Gastos programados

São listados os gastos do mês atual cuja data seja posterior ao dia de hoje. O status não é armazenado no banco; ele é derivado da data.

### Notas fixadas

Notas marcadas como fixadas são exibidas em pequenos cartões, contendo título e uma prévia de até 160 caracteres.

## 5.2. Bloco de notas

A tela usa duas colunas:

- Esquerda: lista das notas, título, prévia e indicador de fixação.
- Direita: editor do título, conteúdo e opção de fixar.

### Criar uma nota

1. Pressione `+ Nova nota`.
2. O programa cria imediatamente uma nota chamada “Nova nota”.
3. O título fica selecionado para digitação.
4. Edite título, conteúdo e fixação.

### Salvamento automático

Não existe botão Salvar. Alterações no título, conteúdo ou checkbox iniciam um temporizador de 500 milissegundos. Quando o usuário para de digitar, a nota é gravada.

Antes de criar outra nota e ao fechar o programa, a nota atual também é salva explicitamente.

Se o título ficar vazio, o banco recebe “Sem título”. A data de atualização é renovada a cada salvamento.

### Ordenação

As notas são exibidas nesta ordem:

1. Fixadas primeiro.
2. Mais recentemente atualizadas primeiro.
3. ID mais recente em caso de empate.

### Exclusão

O botão Excluir pede confirmação e remove a nota definitivamente do banco. Um backup anterior ainda pode conter a nota.

## 5.3. Finanças — modo Gastos

Esse é o modo padrão da aba Finanças.

### Navegação mensal

Os botões `‹` e `›` alternam entre meses e anos. Receitas, gastos, saldo e meta são recalculados para o período selecionado.

### Resumo mensal

A parte superior mostra:

- Receitas: soma das receitas cadastradas no mês.
- Gastos: soma de todos os gastos cadastrados no mês, inclusive futuros.
- Saldo: receitas menos todos os gastos do mês.

O rodapé repete o total de gastos do mês.

### Tabela de gastos

Cada linha contém:

- Data.
- Descrição.
- Categoria.
- Status.
- Valor.
- Ação de remoção.

O status segue a regra:

- `Feito`: data menor ou igual a hoje.
- `Agendado`: data posterior a hoje.

### Adicionar gasto

O formulário exige descrição, categoria e valor maior que zero. Também recebe data e marcador de recorrência. As categorias sugeridas são Moradia, Alimentação, Transporte, Saúde, Lazer, Educação e Outros, mas o campo é editável.

O marcador recorrente é persistido, porém ainda não cria automaticamente o gasto do mês seguinte.

### Remover gasto

O botão Remover pede confirmação e exclui o registro. No estado atual, um gasto não pode ser editado; para corrigir um dado é necessário remover e cadastrar novamente.

### Gerenciar receitas

O botão abre uma janela com todas as receitas do mês selecionado. Cada receita possui:

- Origem, por exemplo Salário, FGTS ou trabalho extra.
- Valor recebido.
- Ação Editar.
- Ação Excluir.

A janela mostra o total recebido. Origem e valor são obrigatórios para novos cadastros. Receitas antigas, criadas antes desse recurso, aparecem como “Não informado” até serem editadas.

As receitas são associadas ao mês, não a um dia específico.

### Definir meta

Uma meta pode ser geral ou vinculada a uma categoria. Ao definir novamente uma meta para o mesmo mês e categoria, a anterior é substituída.

Para uma meta geral, o progresso considera todos os gastos do mês. Para uma meta de categoria, considera apenas gastos cuja categoria seja exatamente igual ao nome salvo na meta.

## 5.4. Finanças — Lista de desejos

O toggle no topo alterna entre Gastos e Lista de desejos.

### Total da lista

O total é a soma do preço mais recente de cada produto. Não é a soma de todo o histórico.

### Adicionar produto

O formulário recebe:

- Nome obrigatório.
- Preço inicial maior que zero.
- Link opcional.

Ao criar o produto, o preço inicial também é inserido como a primeira linha do histórico.

### Preço atual e tendência

O preço atual nunca é sobrescrito. Toda atualização insere uma nova linha com data e hora.

A tendência compara os dois registros mais recentes:

- Seta para baixo: o preço diminuiu.
- Seta para cima: o preço aumentou.
- Seta horizontal: não houve alteração.
- Traço: ainda não existe uma segunda verificação.

### Link do produto

Quando existe link, `Ver produto` solicita ao sistema operacional que abra a URL no navegador padrão.

### Atualizar preço

O botão solicita um novo valor e insere outra verificação no histórico. Isso atualiza automaticamente o preço atual, a variação e o total da lista.

### Exclusão múltipla

1. Pressione Excluir para ativar o modo de seleção.
2. Marque os produtos desejados.
3. Pressione Excluir marcados.
4. Confirme a operação.

Ao excluir um produto, o SQLite remove seu histórico automaticamente por `ON DELETE CASCADE`.

## 5.5. Histórico de preços

`Ver histórico` abre uma janela com duas abas.

### Aba Tabela

Exibe as verificações da mais recente para a mais antiga:

- Data e hora.
- Preço.
- Variação em relação ao registro anterior.
- Botão Excluir.

É permitido excluir uma atualização incorreta. O último registro restante fica protegido, pois cada produto precisa manter um preço atual. Para eliminar também esse último preço, deve-se excluir o próprio produto.

### Aba Gráfico

O gráfico apresenta os preços em ordem cronológica. Os pontos ficam conectados por uma linha e não exibem rótulos permanentes.

Ao passar o cursor sobre a linha ou um ponto, o programa localiza a verificação temporal mais próxima e mostra:

- Data e hora.
- Preço.
- Variação em reais.
- Variação percentual.

Essa busca por proximidade evita falhas quando o Qt fornece uma coordenada interpolada entre dois pontos.

### Escala adaptativa

O eixo horizontal muda conforme o intervalo:

- Menos de um dia: dia, mês, hora e minuto.
- Menos de 90 dias: dia e mês.
- Períodos maiores: mês e ano.

O gráfico também calcula margens horizontais e verticais para evitar pontos colados nas bordas. Registros antigos que possuem apenas a data continuam compatíveis; verificações repetidas no mesmo dia recebem um pequeno espaçamento visual para permanecerem selecionáveis.

## 6. Modelo de dados

## 6.1. `receitas`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `mes_ano` | TEXT | Período no formato `YYYY-MM` |
| `origem` | TEXT | Origem obrigatória; padrão “Não informado” |
| `valor` | REAL | Valor maior ou igual a zero |

## 6.2. `gastos`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `descricao` | TEXT | Obrigatória |
| `categoria` | TEXT | Obrigatória |
| `valor` | REAL | Valor maior ou igual a zero |
| `data` | TEXT | Data ISO `YYYY-MM-DD` |
| `recorrente` | INTEGER | `0` ou `1` |

## 6.3. `metas`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `mes_ano` | TEXT | Período `YYYY-MM` |
| `categoria` | TEXT/NULL | `NULL` representa meta geral |
| `valor_alvo` | REAL | Valor maior ou igual a zero |

## 6.4. `notas`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `titulo` | TEXT | Obrigatório |
| `conteudo` | TEXT | Texto livre |
| `fixada_no_painel` | INTEGER | `0` ou `1` |
| `criada_em` | TEXT | Data e hora ISO |
| `atualizada_em` | TEXT | Data e hora ISO |

## 6.5. `itens_desejo`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `nome_produto` | TEXT | Obrigatório |
| `link` | TEXT/NULL | URL opcional |
| `criado_em` | TEXT | Data e hora ISO |

## 6.6. `historico_preco`

| Campo | Tipo | Regra |
|---|---|---|
| `id` | INTEGER | Chave primária automática |
| `item_id` | INTEGER | Referência ao produto |
| `preco` | REAL | Valor maior ou igual a zero |
| `verificado_em` | TEXT | Data ou data/hora ISO |

A relação usa exclusão em cascata. O índice por produto, data e ID acelera a busca pelos preços mais recentes.

## 7. Armazenamento, backup e exportação

## 7.1. Pasta de dados

O programa usa `platformdirs`, portanto o caminho varia por sistema. No Linux, o padrão atual é:

```text
~/.local/share/FinancasENotas/
├── financas_notas.db
└── backups/
```

O caminho efetivo sempre aparece na barra inferior do aplicativo.

## 7.2. Backup automático

Ao fechar normalmente:

1. A nota atual é salva.
2. O banco é copiado para `backups/`.
3. O nome recebe data e hora.
4. Apenas as 20 cópias mais recentes são mantidas.

Se o backup falhar, o programa informa o motivo e pergunta se o usuário deseja sair mesmo assim.

Para backup em nuvem sem integração adicional, a pasta pode ser sincronizada pelo Google Drive, OneDrive, Dropbox ou serviço equivalente.

## 7.3. Exportação CSV

O botão Exportar dados solicita uma pasta e cria um diretório com data e hora. São gerados seis arquivos:

- `receitas.csv`
- `gastos.csv`
- `metas.csv`
- `notas.csv`
- `itens_desejo.csv`
- `historico_preco.csv`

Os arquivos usam UTF-8 com BOM para facilitar a abertura correta de acentos em planilhas.

Exportar não apaga nem altera o banco.

## 8. Migração e compatibilidade

O banco é criado com `CREATE TABLE IF NOT EXISTS`, permitindo abrir instalações existentes.

A migração atualmente implementada verifica se `receitas.origem` existe. Se não existir, executa `ALTER TABLE` e atribui “Não informado” às receitas antigas.

Registros antigos do histórico podem conter apenas `YYYY-MM-DD`; registros novos usam data e hora ISO. Consultas e gráficos aceitam os dois formatos.

## 9. Instalação e execução para desenvolvimento

Na raiz do projeto:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python main.py
```

Dependências de produção ficam em `requirements.txt`. `requirements-dev.txt` inclui também pytest.

## 10. Testes

Execute:

```bash
.venv/bin/python -m pytest -q
```

Os testes atuais cobrem:

- Formatação monetária brasileira.
- Cálculo do progresso da meta.
- Tendência de aumento, queda ou ausência de histórico.
- CRUD principal de receitas, gastos, notas e desejos.
- Atualização e exclusão segura de preços.
- Exclusão em cascata do produto.
- Migração da origem em um banco legado.

O gráfico e a abertura geral também foram validados em testes de inicialização do Qt no modo offscreen, mas esses testes ainda não fazem parte da suíte pytest permanente.

## 11. Gerar o executável

No Linux:

```bash
.venv/bin/pyinstaller --clean --noconfirm financas_notas.spec
```

O resultado é criado em:

```text
dist/FinancasENotas
```

O arquivo `.spec` inclui os plugins do PySide6 e declara `PySide6.QtCharts` como importação necessária. O build deve ser realizado separadamente em Linux, Windows e macOS.

Avisos sobre `shell32` e `ole32` em um build Linux vêm de caminhos opcionais para Windows. O aviso do plugin TIFF afeta leitura de imagens `.tiff`, não o banco ou os gráficos.

## 12. Regras e decisões importantes

- O aplicativo é local, pessoal e de usuário único.
- Não há login, servidor ou sincronização implementada.
- Valores monetários são armazenados como `REAL`, conforme a especificação inicial.
- Datas são armazenadas em ISO para ordenar corretamente como texto.
- O status do gasto é calculado pela data, não armazenado.
- O preço atual é sempre o registro mais recente do histórico.
- Atualizar preço insere uma linha; nunca sobrescreve o histórico.
- O último preço de um produto não pode ser excluído isoladamente.
- Excluir um produto remove todo o histórico associado.
- O fechamento normal cria um backup; encerramentos forçados podem não criar.

## 13. Limitações conhecidas

- Gastos podem ser criados e removidos, mas ainda não editados.
- O marcador recorrente ainda não gera parcelas ou meses seguintes.
- Metas podem ser definidas/substituídas, mas não há uma janela para listar e excluir todas.
- O painel mostra somente o mês atual e não tem navegação própria.
- Receitas são associadas ao mês, sem data exata ou recorrência.
- Produtos não possuem edição de nome e link depois da criação.
- Não há busca, filtros avançados ou ordenação configurável nas tabelas.
- Não existe importação de CSV nem restauração guiada de backup.
- Não há criptografia do banco nem senha de abertura.
- Não há atualização automática de preços por sites.
- Os testes automatizados ainda não cobrem interações completas da interface.

## 14. Recomendações de evolução

As recomendações abaixo estão organizadas por impacto e dependência.

### Prioridade alta

#### 1. Editar gastos

Reutilizar o formulário de criação preenchendo os valores existentes. É a lacuna mais perceptível no CRUD financeiro e evita remover/recriar lançamentos.

#### 2. Gerenciador completo de metas

Criar uma janela que liste metas gerais e por categoria, permita editar, excluir e copiar para o próximo mês. Isso torna previsível qual meta o painel selecionará.

#### 3. Recorrência real

Transformar o marcador recorrente em uma regra de recorrência com frequência, data final e geração controlada. Deve haver proteção contra duplicação ao abrir o aplicativo várias vezes.

#### 4. Restauração de backup

Adicionar uma tela para listar backups, visualizar data/tamanho, confirmar e restaurar. Antes da restauração, o banco atual deve receber uma cópia de segurança.

### Prioridade média

#### 5. Relatórios por categoria

Adicionar gráfico mensal por categoria, comparação com o mês anterior, média móvel e participação de cada categoria. Um gráfico de barras costuma comunicar receitas versus gastos melhor que incluir recebido, gasto e sobra na mesma pizza.

#### 6. Navegação de mês no painel

Permitir consultar meses anteriores e futuros diretamente no painel, reutilizando a navegação já existente na tela de gastos.

#### 7. Filtros, busca e ordenação

Incluir busca por descrição, filtros de categoria/status, intervalo de datas e ordenação por valor. Para notas, adicionar pesquisa por título e conteúdo.

#### 8. Edição de produtos

Permitir corrigir nome e link sem perder o histórico. Também podem ser adicionados campos de prioridade, loja, observação e preço desejado.

#### 9. Alertas de preço desejado

Quando o preço atual ficar abaixo de um limite definido pelo usuário, destacar o produto e opcionalmente enviar uma notificação local.

#### 10. Importação financeira

Importar CSV de bancos e, futuramente, OFX. A importação deve incluir uma tela de correspondência de colunas e detecção de duplicatas.

### Prioridade técnica

#### 11. Migrações versionadas

Criar uma tabela `schema_version` e scripts incrementais. Isso será importante quando novas colunas e tabelas começarem a se acumular.

#### 12. Valores em centavos inteiros

Embora `REAL` seja aceitável para o uso pessoal previsto, armazenar centavos como `INTEGER` evita pequenos efeitos de ponto flutuante. Essa mudança exige migração cuidadosa.

#### 13. Testes de interface

Adicionar `pytest-qt` para testar criação, edição, exclusão, troca de abas, hover do gráfico e salvamento automático. Também é recomendável testar um build empacotado em integração contínua.

#### 14. Backup consistente pelo SQLite

Usar a API `sqlite3.Connection.backup()` no lugar de cópia simples do arquivo torna o backup robusto mesmo se futuramente existirem conexões longas ou gravações simultâneas.

#### 15. Registro de erros

Criar logs rotativos na pasta de dados, com tratamento global de exceções. Isso permitirá analisar falhas sem depender do terminal, especialmente porque o executável é gerado sem console.

### Recursos opcionais de longo prazo

- Tema claro/escuro configurável.
- Tags e anexos nas notas.
- Parcelamento de compras.
- Contas separadas, como carteira, banco e cartão.
- Fechamento e vencimento de cartão de crédito.
- Planejamento anual e projeção de saldo.
- Exportação de relatório em PDF.
- Sincronização opcional entre dispositivos.
- Atualização manual assistida ou automática de preços, respeitando termos dos sites.
- Senha local e criptografia para usuários que compartilham o computador.

## 15. Sugestão de roadmap

Uma sequência equilibrada seria:

1. Edição de gastos e produtos.
2. Gerenciador completo de metas.
3. Recorrência e parcelamento.
4. Navegação histórica e relatórios por categoria.
5. Restauração de backup e importação CSV/OFX.
6. Testes de interface e logs rotativos.
7. Alertas e automações opcionais.

Essa ordem fecha primeiro as lacunas de CRUD, depois amplia análise e, por fim, adiciona integrações mais complexas.
