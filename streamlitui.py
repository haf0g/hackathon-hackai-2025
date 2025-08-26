import streamlit as st
import json
from dataclasses import dataclass
from typing import List
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import altair as alt

# ------- RAG SYSTEM -------

@dataclass
class ProductItem:
    nom_article: str
    societe_fabricant: str
    prix: float
    stock: int
    description_produit: str
    delai_livraison_moyen: str

class RAGSystem:
    def _init_(self, data_path: str = 'market_stock.json'):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.data = self.load_data(data_path)
        self.embeddings = {}
        self.initialize_embeddings()

    def load_data(self, path: str) -> List[ProductItem]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading knowledge base: {e}")

        items = []
        for entry in raw_data.get('products', []):
            items.append(ProductItem(
                nom_article=entry.get('nom_article', ''),
                societe_fabricant=entry.get('societe_fabricant', ''),
                prix=entry.get('prix', 0.0),
                stock=entry.get('stock', 0),
                description_produit=entry.get('description_produit', ''),
                delai_livraison_moyen=entry.get('delai_livraison_moyen', '')
            ))
        return items

    def initialize_embeddings(self):
        for item in self.data:
            text = f"{item.nom_article} {item.societe_fabricant} {item.prix}€ " \
                   f"{item.stock} unités {item.description_produit} " \
                   f"livraison: {item.delai_livraison_moyen}"
            self.embeddings[item.nom_article] = self.model.encode(text)

    def retrieve_context(self, query: str, k: int = 3) -> str:
        query_emb = self.model.encode(query)
        similarities = [
            (cosine_similarity([query_emb], [self.embeddings[item.nom_article]])[0][0], item)
            for item in self.data
        ]
        top_items = sorted(similarities, key=lambda x: x[0], reverse=True)[:k]

        context = ""
        for sim, item in top_items:
            context += (
                f"Nom de l'article : {item.nom_article}\n"
                f"Fabricant : {item.societe_fabricant}\n"
                f"Prix : {item.prix} €\n"
                f"Stock : {item.stock} unités\n"
                f"Description : {item.description_produit}\n"
                f"Délai de livraison moyen : {item.delai_livraison_moyen}\n\n"
            )
        return context

# ------ CONFIG GROQ ------

GROQ_API_KEY = "gsk___"
groq_client = Groq(api_key=GROQ_API_KEY)

# ------ INITIALISATIONS ------

rag = RAGSystem('knowledge_base.json')

# ------ FONCTION ANALYSE STOCK & REMARQUES ------

def analyze_stock(products: List[ProductItem], seuil_rupture=10):
    remarks = []
    ruptures = [p.nom_article for p in products if p.stock < seuil_rupture]
    if ruptures:
        remarks.append(f"Alerte rupture ou stock faible (< {seuil_rupture}) détectée pour : {', '.join(ruptures)}.")
    else:
        remarks.append("Pas de rupture de stock détectée.")
    return remarks

# ------ STREAMLIT APP ------

st.title("Assistant Insights Produits - Supermarché")

query = st.text_area("Pose ta question sur les produits en stock :", height=100)

if st.button("Générer Insight"):

    if not query.strip():
        st.error("Merci de saisir une requête.")
    else:
        with st.spinner("Analyse et génération en cours..."):
            try:
                # Analyse stock / remarques
                remarks = analyze_stock(rag.data)
                for r in remarks:
                    st.warning(r)

                # Données sous forme DataFrame pour graphiques
                df = pd.DataFrame([{
                    'Nom': p.nom_article,
                    'Fabricant': p.societe_fabricant,
                    'Prix (€)': p.prix,
                    'Stock (unités)': p.stock,
                    'Délai Livraison': p.delai_livraison_moyen
                } for p in rag.data])

                st.subheader("Visualisations des produits")

                # Bar chart stock par produit
                bar_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('Nom', sort='-y'),
                    y='Stock (unités)',
                    color='Fabricant',
                    tooltip=['Nom', 'Fabricant', 'Stock (unités)']
                ).properties(width=700, height=300)
                st.altair_chart(bar_chart)

                # Scatter plot prix vs stock
                scatter = alt.Chart(df).mark_circle(size=100).encode(
                    x='Prix (€)',
                    y='Stock (unités)',
                    color='Fabricant',
                    tooltip=['Nom', 'Prix (€)', 'Stock (unités)', 'Délai Livraison']
                ).properties(width=700, height=300)
                st.altair_chart(scatter)

                # Récupérer contexte pour requête
                context = rag.retrieve_context(query)

                prompt = f"""Tu es un assistant pour un supermarché. Utilise les informations suivantes pour générer des insights sur les produits en stock, leurs fabricants, prix et livraisons :

{context}

Fournis un résumé clair et utile basé sur la requête de l'utilisateur (en français, anglais ou arabe)."""

                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for retail product stock insights."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7,
                )

                generated_text = response.choices[0].message.content.strip()
                st.subheader("Insight généré :")
                st.write(generated_text)

            except Exception as e:

                st.error(f"Erreur lors de la génération : {e}")
