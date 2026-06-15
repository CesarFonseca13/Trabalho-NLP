# 🔎 Busca Semântica de Avaliações (NLP)

### 👉 Acesse o app online: **https://trabalho-nlp-lw2nakkbxysdjuxkaipr3x.streamlit.app/**

---

Sistema de **recuperação semântica de informação**: o usuário digita uma busca em
linguagem natural e o sistema retorna as avaliações de produtos mais parecidas em
**significado** (não em palavras exatas), usando **embeddings vetoriais** e
**similaridade do cosseno**.

Base de dados: [B2W-Reviews01](https://github.com/americanas-tech/b2w-reviews01)
(avaliações reais de e-commerce em português).

## Como rodar localmente

```bash
# 1) Instalar as dependências
pip install -r requirements.txt

# 2) Gerar os embeddings (uma única vez — leva alguns minutos)
python preparar_dados.py

# 3) Abrir o app
streamlit run app.py
```

O navegador abre em `http://localhost:8501`.

## Como publicar online (grátis, via Streamlit Community Cloud)

1. Crie um repositório novo no GitHub e envie estes arquivos:
   `app.py`, `preparar_dados.py`, `requirements.txt`, `.streamlit/config.toml`,
   `reviews_app.csv` e `embeddings.npy`.
   > O dataset original (`B2W-Reviews01.csv`) **não** precisa ir — o app usa só os
   > arquivos `reviews_app.csv` e `embeddings.npy` já prontos (estão no `.gitignore`
   > apenas os arquivos grandes/desnecessários).

2. Acesse <https://share.streamlit.io>, faça login com o GitHub e clique em
   **New app**.

3. Aponte para o repositório e o arquivo `app.py`. Clique em **Deploy**.

4. Pronto: você recebe um link público (ex.: `https://seu-app.streamlit.app`).

## Arquivos do projeto

| Arquivo | O que é |
|---|---|
| `nlp_portugues.ipynb` | Notebook da análise (EDA, limpeza, embeddings, clusters, busca) |
| `preparar_dados.py` | Gera os embeddings e salva em disco (roda uma vez) |
| `app.py` | Frontend Streamlit da busca semântica |
| `reviews_app.csv` | Amostra de avaliações indexadas pelo app |
| `embeddings.npy` | Embeddings já calculados dessas avaliações |
