# DashboardNBA
Dashboard NBA: A Revolução da Bola de 3 (2015–2025)
Este projeto é um dashboard interativo em Streamlit que analisa a evolução das bolas de 3 pontos na NBA, com foco nas temporadas de 2014–15 a 2023–24.
O app coleta dados da API oficial da NBA via nba_api, salva em arquivos CSV locais e exibe visualizações e métricas comparando a liga com os times campeões.

Funcionalidades
Coleta automática de dados da NBA

Usa o endpoint LeagueDashTeamStats da biblioteca nba_api para baixar estatísticas por time e temporada da temporada regular.

Salva um CSV consolidado com todas as temporadas em data/processed_team_stats_2015_2025.csv.

Cria um CSV com os campeões de cada temporada em data/champions.csv.

Processamento e criação de métricas

Mantém colunas principais: temporada, time, jogos, vitórias, derrotas, bolas de 3 convertidas, tentadas, aproveitamento e pontos.

Calcula:

Bolas de 3 por jogo (THREES_PER_GAME)

Tentativas de 3 por jogo (THREES_ATT_PER_GAME)

Pontos vindos de 3 (POINTS_FROM_3)

Percentual dos pontos totais vindos de 3 (PERCENT_POINTS_3)

Cache de dados

Usa @st.cache_data para carregar os dados apenas na primeira execução, evitando novas requisições à API sempre que o app é recarregado.

Filtros interativos na barra lateral

Seleção de temporada.

Seleção de um ou mais times da temporada escolhida.

Filtro mínimo de aproveitamento de 3 pontos (em porcentagem).

Métricas de destaque da temporada selecionada

Média de tentativas de 3 por jogo na liga.

Aproveitamento médio de 3 pontos da liga.

Aproveitamento de 3, tentativas de 3 por jogo e percentual dos pontos vindos de 3 do time campeão da temporada (quando presente nos dados).

Visualizações

Gráfico de barras: ranking dos times com mais bolas de 3 convertidas por jogo na temporada filtrada.

Gráfico de linhas histórico:

Média de tentativas de 3 por jogo da liga (todas as equipes).

Tentativas de 3 por jogo do campeão em cada temporada.

Tabela detalhada e exportação

Tabela interativa com estatísticas filtradas (vitórias, derrotas, bolas de 3 por jogo, tentativas, aproveitamento, % dos pontos de 3, flag de campeão).

Botão para baixar em CSV os dados filtrados da temporada selecionada.

Contexto do projeto

Demonstra um fluxo completo de Ciência de Dados:

Coleta (API NBA)

Armazenamento em CSV

Limpeza e transformação

Visualização interativa com Streamlit

Estrutura principal do código
Configuração geral

Diretório data/ para armazenamento dos CSVs.

Lista de temporadas (SEASONS) e lista dos campeões (CHAMPIONS_DATA).

Função get_team_stats_for_season(season)

Chama LeagueDashTeamStats para uma temporada específica.

Retorna um DataFrame com as estatísticas do time e adiciona a coluna SEASON.

Função generate_csv_files()

Cria o diretório data/ se não existir.

Faz loop pelas temporadas em SEASONS, baixa os dados e concatena em um único DataFrame.

Seleciona apenas as colunas relevantes e cria novas métricas relacionadas a bolas de 3.

Salva o CSV processado de estatísticas e o CSV dos campeões.

Função ensure_data_files()

Verifica se os arquivos processed_team_stats_2015_2025.csv e champions.csv existem.

Se não existirem, chama generate_csv_files() para gerá-los.

Função load_data() (com @st.cache_data)

Garante que os CSVs existam.

Lê os arquivos de estatísticas e campeões, faz o merge pela coluna SEASON.

Cria a coluna booleana IS_CHAMPION indicando se o time é o campeão da temporada.

Bloco principal do app Streamlit

Configura layout e título do app (st.set_page_config, st.title, st.markdown).

Carrega os dados com spinner de carregamento.

Cria os filtros na sidebar.

Aplica filtros por temporada, time e aproveitamento mínimo de 3 pontos.

Ajusta FG3_PCT para porcentagem se estiver em escala 0–1.

Calcula métricas agregadas da liga e do campeão.

Exibe:

Métricas em colunas com st.metric.

Gráfico de barras (st.bar_chart) para bolas de 3 por jogo.

Gráfico de linhas (st.line_chart) para evolução histórica liga x campeões.

Tabela com st.dataframe.

Botão de download de CSV com st.download_button.

Requisitos
Crie um arquivo requirements.txt com, por exemplo:

text
streamlit
pandas
nba_api
(Adapte versões específicas se necessário.)

Passo a passo para rodar o projeto
Clonar ou copiar o projeto

Salve o arquivo Python (por exemplo, app.py) e este README.md em uma pasta do seu computador.

Criar e ativar um ambiente virtual (opcional, mas recomendado)

No terminal/prompt de comando:

bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
Instalar as dependências

bash
pip install -r requirements.txt
Executar o app Streamlit

bash
streamlit run app.py
Substitua app.py pelo nome do arquivo Python que contém o código.

Acessar o dashboard

Após rodar o comando, o Streamlit informará um endereço local (geralmente http://localhost:8501).

Abra esse endereço no navegador.

Primeira execução (coleta de dados)

Na primeira vez, o app pode demorar um pouco mais porque:

Vai chamar a API da NBA para cada temporada em SEASONS.

Vai gerar e salvar os CSVs em data/.

Nas próximas execuções, o app lerá os CSVs locais e usará o cache, ficando bem mais rápido.

Usando o dashboard

Na barra lateral, escolha a temporada desejada.

Se quiser, selecione apenas alguns times da temporada.

Ajuste o aproveitamento mínimo de 3 pontos para filtrar equipes com bom desempenho no perímetro.

Observe:

As métricas da liga e do campeão.

O ranking de bolas de 3 por jogo por time.

A evolução histórica da dependência da bola de 3 na liga e nos campeões.

A tabela detalhada de estatísticas.

Use o botão de download para exportar o CSV filtrado.
