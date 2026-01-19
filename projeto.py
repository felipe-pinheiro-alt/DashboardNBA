import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import LeagueDashTeamStats
import os

# ========== CONFIGURAÇÃO DA PÁGINA ==========
st.set_page_config(
    page_title="NBA Analytics Hub",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CSS CUSTOMIZADO ==========
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Tema geral */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Título principal */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards de métricas */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(102, 126, 234, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    div[data-testid="metric-container"] label {
        color: #a0aec0 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #667eea !important;
        font-weight: 700;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Selectbox e inputs */
    .stSelectbox, .stMultiSelect, .stSlider {
        color: white;
    }
    
    /* Tabela */
    div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Headers de seção */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-left: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #e2e8f0;
    }
    
    /* Gráficos */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== CONSTANTES ==========
DATA_DIR = "data"
SEASONS = [
    "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
    "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"
]
CHAMPIONS_DATA = {
    "2014-15": "Golden State Warriors",
    "2015-16": "Cleveland Cavaliers",
    "2016-17": "Golden State Warriors",
    "2017-18": "Golden State Warriors",
    "2018-19": "Toronto Raptors",
    "2019-20": "Los Angeles Lakers",
    "2020-21": "Milwaukee Bucks",
    "2021-22": "Golden State Warriors",
    "2022-23": "Denver Nuggets",
    "2023-24": "Boston Celtics"
}

# ========== FUNÇÕES DE COLETA E PROCESSAMENTO ==========
def get_team_stats_for_season(season):
    """Busca estatísticas dos times para uma temporada específica"""
    stats = LeagueDashTeamStats(season=season, per_mode_detailed="PerGame")
    df = stats.get_data_frames()[0]
    df["SEASON"] = season
    return df

def generate_csv_files():
    """Gera os arquivos CSV com dados da NBA"""
    os.makedirs(DATA_DIR, exist_ok=True)
    all_data = []
    
    for season in SEASONS:
        df_season = get_team_stats_for_season(season)
        all_data.append(df_season)
    
    df_all = pd.concat(all_data, ignore_index=True)
    
    cols = [
        "SEASON", "TEAM_NAME", "GP", "W", "L",
        "FG3M", "FG3A", "FG3_PCT", "PTS"
    ]
    df_all = df_all[cols]
    
    # Criar métricas calculadas
    df_all["THREES_PER_GAME"] = df_all["FG3M"]
    df_all["THREES_ATT_PER_GAME"] = df_all["FG3A"]
    df_all["POINTS_FROM_3"] = df_all["FG3M"] * 3
    df_all["PERCENT_POINTS_3"] = (df_all["POINTS_FROM_3"] / df_all["PTS"]) * 100
    
    processed_file = os.path.join(DATA_DIR, "processed_team_stats_2015_2025.csv")
    df_all.to_csv(processed_file, index=False)
    
    # CSV dos campeões
    champions_df = pd.DataFrame(list(CHAMPIONS_DATA.items()), columns=["SEASON", "CHAMPION_TEAM"])
    champions_file = os.path.join(DATA_DIR, "champions.csv")
    champions_df.to_csv(champions_file, index=False)

def ensure_data_files():
    """Garante que os arquivos de dados existam"""
    stats_file = os.path.join(DATA_DIR, "processed_team_stats_2015_2025.csv")
    champs_file = os.path.join(DATA_DIR, "champions.csv")
    
    if not os.path.exists(stats_file) or not os.path.exists(champs_file):
        generate_csv_files()

@st.cache_data
def load_data():
    """Carrega os dados com cache"""
    ensure_data_files()
    
    stats_file = os.path.join(DATA_DIR, "processed_team_stats_2015_2025.csv")
    champs_file = os.path.join(DATA_DIR, "champions.csv")
    
    df_stats = pd.read_csv(stats_file)
    df_champs = pd.read_csv(champs_file)
    
    df = df_stats.merge(df_champs, on="SEASON", how="left")
    df["IS_CHAMPION"] = df["TEAM_NAME"] == df["CHAMPION_TEAM"]
    
    return df

# ========== INTERFACE PRINCIPAL ==========
def main():
    # Cabeçalho
    st.markdown('<h1 class="main-title">🏀 NBA ANALYTICS HUB</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análise Avançada da Revolução dos 3 Pontos (2015-2025)</p>', unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner("🔄 Carregando dados da NBA..."):
        df = load_data()
    
    # ========== SIDEBAR ==========
    st.sidebar.markdown("## ⚙️ Filtros")
    st.sidebar.markdown("---")
    
    # Filtro de temporada
    selected_season = st.sidebar.selectbox(
        "📅 Temporada",
        options=sorted(df["SEASON"].unique(), reverse=True),
        index=0
    )
    
    # Filtrar dados pela temporada
    df_season = df[df["SEASON"] == selected_season].copy()
    
    # Filtro de times
    all_teams = sorted(df_season["TEAM_NAME"].unique())
    selected_teams = st.sidebar.multiselect(
        "🏆 Times",
        options=all_teams,
        default=all_teams
    )
    
    # Filtro de aproveitamento
    min_fg3_pct = st.sidebar.slider(
        "🎯 Aproveitamento Mínimo de 3PT (%)",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )
    
    # Aplicar filtros
    df_filtered = df_season[df_season["TEAM_NAME"].isin(selected_teams)]
    
    # Ajustar FG3_PCT se estiver em escala 0-1
    if df_filtered["FG3_PCT"].max() <= 1:
        df_filtered["FG3_PCT"] = df_filtered["FG3_PCT"] * 100
    
    df_filtered = df_filtered[df_filtered["FG3_PCT"] >= min_fg3_pct]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Sobre o Dashboard")
    st.sidebar.markdown(
        '<div class="info-box">Dashboard interativo que analisa a evolução das bolas de 3 pontos na NBA.</div>',
        unsafe_allow_html=True
    )
    
    # ========== MÉTRICAS PRINCIPAIS ==========
    st.markdown('<h2 class="section-header">📈 Métricas da Temporada</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_threes_att = df_filtered["THREES_ATT_PER_GAME"].mean()
        st.metric(
            label="Tentativas de 3PT/Jogo",
            value=f"{avg_threes_att:.1f}",
            delta="Liga"
        )
    
    with col2:
        avg_fg3_pct = df_filtered["FG3_PCT"].mean()
        st.metric(
            label="Aproveitamento Médio",
            value=f"{avg_fg3_pct:.1f}%",
            delta="3 Pontos"
        )
    
    with col3:
        champion_row = df_filtered[df_filtered["IS_CHAMPION"] == True]
        if not champion_row.empty:
            champ_fg3_pct = champion_row.iloc[0]["FG3_PCT"]
            st.metric(
                label="Campeão - 3PT%",
                value=f"{champ_fg3_pct:.1f}%",
                delta=f"+{(champ_fg3_pct - avg_fg3_pct):.1f}%"
            )
        else:
            st.metric(label="Campeão - 3PT%", value="N/A")
    
    with col4:
        if not champion_row.empty:
            champ_pct_points = champion_row.iloc[0]["PERCENT_POINTS_3"]
            st.metric(
                label="% Pontos do 3PT",
                value=f"{champ_pct_points:.1f}%",
                delta="Campeão"
            )
        else:
            st.metric(label="% Pontos do 3PT", value="N/A")
    
    # ========== GRÁFICO DE BARRAS ==========
    st.markdown('<h2 class="section-header">🎯 Top Times em 3 Pontos</h2>', unsafe_allow_html=True)
    
    df_top = df_filtered.nlargest(10, "THREES_PER_GAME")[["TEAM_NAME", "THREES_PER_GAME"]].set_index("TEAM_NAME")
    st.bar_chart(df_top, color="#667eea")
    
    # ========== GRÁFICO DE LINHA - EVOLUÇÃO ==========
    st.markdown('<h2 class="section-header">📊 Evolução Histórica</h2>', unsafe_allow_html=True)
    
    df_league_avg = df.groupby("SEASON")["THREES_ATT_PER_GAME"].mean().reset_index()
    df_league_avg.columns = ["SEASON", "Liga - Média"]
    
    df_champ = df[df["IS_CHAMPION"] == True][["SEASON", "THREES_ATT_PER_GAME"]]
    df_champ.columns = ["SEASON", "Campeão"]
    
    df_evolution = df_league_avg.merge(df_champ, on="SEASON", how="left").set_index("SEASON")
    st.line_chart(df_evolution)
    
    # ========== TABELA DETALHADA ==========
    st.markdown('<h2 class="section-header">📋 Dados Detalhados</h2>', unsafe_allow_html=True)
    
    display_cols = [
        "TEAM_NAME", "W", "L", "THREES_PER_GAME", "THREES_ATT_PER_GAME",
        "FG3_PCT", "PERCENT_POINTS_3", "IS_CHAMPION"
    ]
    df_display = df_filtered[display_cols].copy()
    df_display = df_display.rename(columns={
        "TEAM_NAME": "Time",
        "W": "Vitórias",
        "L": "Derrotas",
        "THREES_PER_GAME": "3PT/Jogo",
        "THREES_ATT_PER_GAME": "Tentativas 3PT/Jogo",
        "FG3_PCT": "3PT %",
        "PERCENT_POINTS_3": "% Pontos do 3PT",
        "IS_CHAMPION": "Campeão"
    })
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # ========== DOWNLOAD ==========
    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Baixar Dados em CSV",
        data=csv,
        file_name=f"nba_stats_{selected_season}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
