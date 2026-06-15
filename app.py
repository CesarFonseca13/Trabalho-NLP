"""
Busca Semântica de Avaliações de Produtos (NLP) — frontend em Streamlit.

O app carrega os embeddings já calculados (pelo preparar_dados.py), recebe uma
consulta em linguagem natural e devolve as avaliações mais parecidas em SIGNIFICADO,
usando a similaridade do cosseno.

Para rodar:
  1) python preparar_dados.py      (uma vez, para gerar reviews_app.csv e embeddings.npy)
  2) streamlit run app.py
"""

import html
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer

# ----------------------------------------------------------------------------
# Configuração geral da página
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Busca Semântica de Avaliações",
    page_icon="🔎",
    layout="wide",
)

MODELO = "paraphrase-multilingual-MiniLM-L12-v2"


# ----------------------------------------------------------------------------
# Carregamento (em cache para não repetir a cada interação)
# ----------------------------------------------------------------------------
@st.cache_resource
def carregar_modelo():
    # O mesmo modelo usado para gerar os embeddings -> garante coerência na busca
    return SentenceTransformer(MODELO)


@st.cache_data
def carregar_dados():
    df = pd.read_csv("reviews_app.csv")
    embeddings = np.load("embeddings.npy")
    return df, embeddings


# ----------------------------------------------------------------------------
# Função de busca semântica (o coração do sistema)
# ----------------------------------------------------------------------------
def buscar(query, top_n, categorias):
    # transforma a consulta no mesmo espaço vetorial das avaliações
    q = modelo.encode([query], normalize_embeddings=True)[0]

    # como tudo está normalizado, a similaridade do cosseno é só um produto escalar
    similaridades = embeddings @ q

    # ordena do mais parecido para o menos parecido
    ordem = np.argsort(similaridades)[::-1]

    resultados = []
    for i in ordem:
        # aplica o filtro de categoria, se o usuário escolheu alguma
        if categorias and df.iloc[i]["site_category_lv1"] not in categorias:
            continue
        resultados.append((int(i), float(similaridades[i])))
        if len(resultados) >= top_n:
            break
    return resultados


# ----------------------------------------------------------------------------
# Pequenos ajudantes visuais
# ----------------------------------------------------------------------------
def estrelas(nota):
    nota = int(nota)
    return "★" * nota + "☆" * (5 - nota)


def cor_similaridade(s):
    if s >= 0.70:
        return "#16a34a"  # verde  -> bem parecido
    if s >= 0.50:
        return "#d97706"  # laranja -> parecido
    return "#64748b"      # cinza  -> pouco parecido


def render_card(linha, similaridade):
    cat = html.escape(str(linha["site_category_lv1"]))
    titulo = html.escape(str(linha["review_title"]))
    texto = html.escape(str(linha["review_text"]))
    nota = linha["overall_rating"]
    cor = cor_similaridade(similaridade)
    pct = similaridade * 100

    st.markdown(
        f"""
        <div class="card">
          <div class="card-top">
            <span class="badge">{cat}</span>
            <span class="stars">{estrelas(nota)}</span>
            <span class="sim" style="background:{cor}">{pct:.1f}% similar</span>
          </div>
          <div class="card-title">{titulo}</div>
          <div class="card-text">{texto}</div>
          <div class="bar"><div class="bar-fill" style="width:{pct:.0f}%;background:{cor}"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Estilo (CSS) para deixar bonito
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .hero {
        background: linear-gradient(120deg, #6C5CE7 0%, #8E7BFF 50%, #00C2C7 100%);
        padding: 34px 38px; border-radius: 18px; color: #fff; margin-bottom: 8px;
      }
      .hero h1 { margin: 0; font-size: 2.1rem; }
      .hero p  { margin: 8px 0 0 0; opacity: .92; font-size: 1.02rem; }

      .card {
        background: #fff; border: 1px solid #ece9fb; border-radius: 14px;
        padding: 16px 18px; margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(108,92,231,.06);
      }
      .card-top { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }
      .badge { background: #F4F2FF; color: #6C5CE7; font-weight: 600;
               padding: 3px 10px; border-radius: 999px; font-size: .8rem; }
      .stars { color: #f59e0b; letter-spacing: 2px; font-size: .95rem; }
      .sim { color: #fff; font-weight: 700; font-size: .78rem;
             padding: 3px 10px; border-radius: 999px; margin-left: auto; }
      .card-title { font-weight: 700; font-size: 1.02rem; color: #1E1B2E; margin-bottom: 4px; }
      .card-text  { color: #475569; font-size: .94rem; line-height: 1.45; }
      .bar { background: #eef0f4; height: 7px; border-radius: 999px; margin-top: 12px; overflow: hidden; }
      .bar-fill { height: 100%; border-radius: 999px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Carrega tudo
# ----------------------------------------------------------------------------
try:
    modelo = carregar_modelo()
    df, embeddings = carregar_dados()
except FileNotFoundError:
    st.error(
        "Arquivos de dados não encontrados. Rode antes:  **python preparar_dados.py**"
    )
    st.stop()


# ----------------------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>🔎 Busca Semântica de Avaliações</h1>
      <p>Pesquise por <b>significado</b>, não por palavras exatas. O sistema usa
      embeddings vetoriais para recuperar as avaliações mais parecidas com a sua busca.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Métricas rápidas sobre a base indexada
c1, c2, c3 = st.columns(3)
c1.metric("Avaliações indexadas", f"{len(df):,}".replace(",", "."))
c2.metric("Dimensões do embedding", embeddings.shape[1])
c3.metric("Modelo", "MiniLM multilíngue")


# ----------------------------------------------------------------------------
# Barra lateral: opções de busca
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Opções")
    top_n = st.slider("Quantos resultados mostrar", 5, 20, 10)

    cats = sorted(df["site_category_lv1"].dropna().unique())
    categoria = st.selectbox(
        "Filtrar por categoria",
        ["Todas as categorias"] + list(cats),
    )
    # vira lista vazia (sem filtro) quando o usuário deixa em "Todas as categorias"
    categorias = [] if categoria == "Todas as categorias" else [categoria]

    st.divider()
    st.caption(
        "Trabalho de NLP — recuperação semântica de informação com "
        "embeddings vetoriais e similaridade do cosseno."
    )


# ----------------------------------------------------------------------------
# Caixa de busca + exemplos clicáveis
# ----------------------------------------------------------------------------
if "query" not in st.session_state:
    st.session_state.query = "o produto chegou quebrado e com defeito"


def usar_exemplo(texto):
    st.session_state.query = texto


st.write("**Experimente um exemplo:**")
exemplos = [
    "o produto chegou quebrado e com defeito",
    "demorou muito para entregar",
    "ótimo custo benefício, vale a pena",
    "veio faltando peças na caixa",
    "fácil de instalar e de usar",
]
cols = st.columns(len(exemplos))
for col, ex in zip(cols, exemplos):
    col.button(ex, on_click=usar_exemplo, args=(ex,), use_container_width=True)

query = st.text_input(
    "Digite sua busca:",
    key="query",
    placeholder="Ex.: a bateria descarrega muito rápido",
)


# ----------------------------------------------------------------------------
# Resultados
# ----------------------------------------------------------------------------
if query.strip():
    resultados = buscar(query, top_n, categorias)

    if not resultados:
        st.warning("Nenhuma avaliação encontrada com esse filtro de categoria.")
    else:
        st.subheader(f"Top {len(resultados)} avaliações mais parecidas")
        for i, sim in resultados:
            render_card(df.iloc[i], sim)
else:
    st.info("Digite algo acima (ou clique em um exemplo) para ver os resultados.")
