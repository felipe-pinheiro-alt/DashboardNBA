import os
import time
import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import leaguedashteamstats

# ------------------------ CONFIG GERAL ------------------------
DATA_DIR = "data"
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_team_stats_2015_2025.csv")
CHAMPIONS_FILE = os.path.join(DATA_DIR, "champions.csv")

SEASONS = [
    "2014-15",
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
]

CHAMPIONS_DATA = [
    ("2014-15", "Golden State Warriors"),
    ("2015-16", "Cleveland Cavaliers"),
    ("2016-17", "Golden State Warriors"),
    ("2017-18", "Golden State Warriors"),
    ("2018-19", "Toronto Raptors"),
    ("2019-20", "Los Angeles Lakers"),
    ("2020-21", "Milwaukee Bucks"),
    ("2021-22", "Golden State Warriors"),
    ("2022-23", "Denver Nuggets"),
    ("2023-24", "Boston Celtics"),
]

# ------------------------ FUNÇÕES DE DADOS ------------------------
def get_team_stats_for_season(season: str) -> pd.DataFrame:
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        season_type_all_star="Regular Season",
        measure_type_detailed_defense="Base",
    )
    df = stats.get_data_frames()[0]
    df["SEASON"] = season
    return df

def generate_csv_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    all_seasons = []
    for s in SEASONS:
        print(f"Baixando dados da temporada {s}...")
        df_s = get_team_stats_for_season(s)
        all_seasons.append(df_s)
        time.sleep(1.5)

    df_all = pd.concat(all_seasons, ignore_index=True)

    cols_keep = [
        "SEASON",
        "TEAM_ID",
        "TEAM_NAME",
        "GP",
        "W",
        "L",
        "FG3M",
        "FG3A",
        "FG3_PCT",
        "PTS",
    ]
    df_all = df_all[cols_keep]

    df_all["THREES_PER_GAME"] = df_all["FG3M"] / df_all["GP"]
    df_all["THREES_ATT_PER_GAME"] = df_all["FG3A"] / df_all["GP"]
    df_all["POINTS_FROM_3"] = df_all["FG3M"] * 3
    df_all["PERCENT_POINTS_3"] = df_all["POINTS_FROM_3"] / df_all["PTS"]

    df_all.to_csv(PROCESSED_FILE, index=False, encoding="utf-8-sig")

    df_champ = pd.DataFrame(CHAMPIONS_DATA, columns=["SEASON", "CHAMPION_TEAM"])
    df_champ.to_csv(CHAMPIONS_FILE, index=False, encoding="utf-8-sig")

def ensure_data_files():
    need_generate = False
    if not os.path.exists(PROCESSED_FILE):
        need_generate = True
    if not os.path.exists(CHAMPIONS_FILE):
        need_generate = True
    if need_generate:
        generate_csv_files()

@st.cache_data
def load_data():
    ensure_data_files()
    df_stats = pd.read_csv(PROCESSED_FILE)
    df_champ = pd.read_csv(CHAMPIONS_FILE)
    df = df_stats.merge(df_champ, on="SEASON", how="left")
    df["IS_CHAMPION"] = df["TEAM_NAME"] == df["CHAMPION_TEAM"]
    return df

# ------------------------ STREAMLIT APP ------------------------
st.set_page_config(
    page_title="Dashboard NBA - Bola de 3",
    page_icon="🏀",
    layout="wide"
)

st.title("Dashboard NBA: A Revolução da Bola de 3 (2015–2025)")
st.markdown(
    """
    Este dashboard explora como o jogo de 3 pontos evoluiu na NBA nas últimas temporadas, 
    com foco em médias da liga e desempenho dos campeões.
    """
)

with st.spinner("Carregando dados da NBA (pode levar alguns segundos na primeira vez)..."):
    df = load_data()

st.sidebar.header("Filtros")

seasons = sorted(df["SEASON"].unique())
selected_season = st.sidebar.selectbox("Selecione a temporada", seasons, index=len(seasons)-1)

teams_in_season = df.loc[df["SEASON"] == selected_season, "TEAM_NAME"].unique()
selected_teams = st.sidebar.multiselect(
    "Selecione times (opcional)",
    sorted(teams_in_season),
    default=list(teams_in_season),
)

min_3pct = st.sidebar.slider(
    "Aproveitamento mínimo de 3 pontos (%)",
    min_value=0.0,
    max_value=60.0,
    value=30.0,
    step=1.0,
)

st.sidebar.markdown(
    """
    **Sobre os dados**  
    - Estatísticas por time e temporada da NBA  
    - Foco em arremessos de 3 pontos e desempenho dos campeões  
    """
)

df_season = df[df["SEASON"] == selected_season].copy()
if selected_teams:
    df_season = df_season[df_season["TEAM_NAME"].isin(selected_teams)]

if df_season["FG3_PCT"].max() <= 1:
    df_season["FG3_PCT"] = df_season["FG3_PCT"] * 100

df_season = df_season[df_season["FG3_PCT"] >= min_3pct]

league_threes_att_pg = df_season["THREES_ATT_PER_GAME"].mean()
league_3pct = df_season["FG3_PCT"].mean()

champ_row = df_season[df_season["IS_CHAMPION"] == True]
if not champ_row.empty:
    champ_team = champ_row["TEAM_NAME"].iloc[0]
    champ_3pct = champ_row["FG3_PCT"].iloc[0]
    champ_threes_att_pg = champ_row["THREES_ATT_PER_GAME"].iloc[0]
    champ_percent_points_3 = champ_row["PERCENT_POINTS_3"].iloc[0]
else:
    champ_team = "Desconhecido"
    champ_3pct = None
    champ_threes_att_pg = None
    champ_percent_points_3 = None

st.subheader(f"Métricas de destaque - Temporada {selected_season}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Média de tentativas de 3 por jogo (liga)",
    f"{league_threes_att_pg:.1f}",
)
col2.metric(
    "Aproveitamento médio de 3 pontos (liga)",
    f"{league_3pct:.1f}%",
)

if champ_3pct is not None:
    col3.metric(
        f"Aproveitamento de 3 do campeão ({champ_team})",
        f"{champ_3pct:.1f}%",
    )
    col4.metric(
        "% dos pontos do campeão vindos de 3",
        f"{champ_percent_points_3*100:.1f}%"
        if champ_percent_points_3 <= 1
        else f"{champ_percent_points_3:.1f}%",
    )
else:
    col3.metric("Campeão", "Dados indisponíveis")
    col4.metric("% pontos de 3 (campeão)", "Dados indisponíveis")

st.subheader("Times com mais bolas de 3 por jogo na temporada selecionada")

df_rank = df_season.sort_values("THREES_PER_GAME", ascending=False)

st.bar_chart(
    data=df_rank,
    x="TEAM_NAME",
    y="THREES_PER_GAME",
    height=400,
)

st.markdown(
    """
    O gráfico acima mostra quais equipes mais convertem bolas de 3 por jogo, 
    permitindo comparar o campeão com o restante da liga.
    """
)

st.subheader("Evolução histórica da tentativa de bolas de 3 (liga x campeões)")

df_league_trend = (
    df.groupby("SEASON", as_index=False)
    .agg({"THREES_ATT_PER_GAME": "mean"})
    .rename(columns={"THREES_ATT_PER_GAME": "LEAGUE_THREES_ATT_PG"})
)

df_champ_trend = (
    df[df["IS_CHAMPION"] == True]
    [["SEASON", "THREES_ATT_PER_GAME"]]
    .rename(columns={"THREES_ATT_PER_GAME": "CHAMP_THREES_ATT_PG"})
)

df_trend = df_league_trend.merge(df_champ_trend, on="SEASON", how="left")
trend_chart_data = df_trend.set_index("SEASON")[["LEAGUE_THREES_ATT_PG", "CHAMP_THREES_ATT_PG"]]

st.line_chart(trend_chart_data, height=400)

st.markdown(
    """
    Essa série histórica compara a média de tentativas de 3 pontos por jogo de todas as equipes 
    com a média do time campeão em cada temporada, evidenciando a importância crescente da bola de 3.
    """
)

st.subheader("Tabela de estatísticas detalhadas (dados filtrados)")

st.dataframe(
    df_season[
        [
            "TEAM_NAME",
            "SEASON",
            "W",
            "L",
            "THREES_PER_GAME",
            "THREES_ATT_PER_GAME",
            "FG3_PCT",
            "PERCENT_POINTS_3",
            "IS_CHAMPION",
        ]
    ].sort_values("THREES_PER_GAME", ascending=False),
    use_container_width=True,
)

csv_download = df_season.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Baixar dados filtrados em CSV",
    data=csv_download,
    file_name=f"nba_stats_{selected_season}.csv",
    mime="text/csv",
)

st.markdown("---")
st.markdown(
    """
    **Contexto do projeto**  
    Este dashboard foi desenvolvido como parte de um projeto de Ciência de Dados, 
    envolvendo coleta via API da NBA, armazenamento em arquivos locais (.csv), 
    limpeza e transformação dos dados e criação de visualizações interativas em Streamlit.
    """
)
