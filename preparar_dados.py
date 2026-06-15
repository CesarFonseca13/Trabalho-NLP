"""
Script de preparação (rodar UMA vez, localmente).

Ele faz o trabalho pesado fora do app: lê o dataset, limpa, escolhe uma amostra,
calcula os embeddings com o modelo multilíngue e salva tudo em disco.

Saídas geradas:
  - reviews_app.csv   -> as avaliações da amostra (texto, categoria, nota, título)
  - embeddings.npy    -> a matriz de embeddings (já normalizados) dessas avaliações

Depois disso, o app (app.py) só carrega esses dois arquivos e faz a busca,
sem precisar recalcular nada. É o que deixa o app rápido e leve para ficar online.
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Quantas avaliações vamos indexar no app (quanto maior, melhor a busca, porém mais pesado)
TAMANHO_AMOSTRA = 8000

print("1/4 - Carregando o dataset...")
df = pd.read_csv("B2W-Reviews01.csv", low_memory=False)

# Mantém só o que o app precisa e remove avaliações sem texto
df = df.dropna(subset=["review_text"]).reset_index(drop=True)
df = df[["site_category_lv1", "overall_rating", "review_title", "review_text"]]

# Tira uma amostra aleatória (random_state fixo para ser reproduzível)
df = df.sample(TAMANHO_AMOSTRA, random_state=42).reset_index(drop=True)
print(f"    {len(df)} avaliações selecionadas.")

print("2/4 - Carregando o modelo de embeddings (pode baixar ~470 MB na 1a vez)...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

print("3/4 - Calculando os embeddings (essa é a parte demorada)...")
# normalize_embeddings=True deixa os vetores prontos para a similaridade do cosseno
# (assim, no app, a similaridade vira um simples produto escalar -> bem rápido)
embeddings = model.encode(
    df["review_text"].tolist(),
    show_progress_bar=True,
    normalize_embeddings=True,
).astype("float32")

print("4/4 - Salvando os arquivos...")
df.to_csv("reviews_app.csv", index=False)
np.save("embeddings.npy", embeddings)

print("\nPronto! Gerados: reviews_app.csv e embeddings.npy")
print("Agora rode o app com:  streamlit run app.py")
