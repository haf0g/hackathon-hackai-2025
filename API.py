from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from typing import List, Dict
from dataclasses import dataclass
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Setup Flask
app = Flask(_name_)
CORS(app)

# Load Groq Client
GROQ_API_KEY = "groq_api_here"
groq_client = Groq(api_key=GROQ_API_KEY)

# ------------------ RAG SYSTEM FOR MARKET PRODUCTS ------------------

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

# Initialize RAG
rag = RAGSystem('knowledge_base.json')

# ------------------ API ROUTES ------------------

@app.route('/generate_insight', methods=['POST'])
def generate_insight():
    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({'error': 'Query is required'}), 400

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
        return jsonify({'insight': generated_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ RUN SERVER ------------------

if _name_ == '_main_':
    app.run(host="0.0.0.0", port=5000, debug=True)
