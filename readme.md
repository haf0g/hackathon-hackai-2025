# Retail Product Insights Assistant 🛒

A comprehensive RAG (Retrieval-Augmented Generation) system for supermarket product analysis, featuring:
- **Telegram bot** for conversational interface
- **Flask API** for RAG functionality
- **Streamlit app** for interactive visualizations

## 📁 Project Structure
retail-insight-assistant/

├── bot.py # Telegram bot implementation 

├── API.py # Flask RAG API server

├── streamlitui.py # Streamlit interactive dashboard

├── knowledge_base.json # Product database (sample provided)

└── requirements.txt # Python dependencies


## 🛠️ Features

### Telegram Bot
- Natural language queries about products
- Real-time stock analysis
- Direct messaging interface

### Flask RAG API
- Product embeddings with Sentence Transformers
- Contextual retrieval from knowledge base
- Integration with Groq's Llama 3 model
- RESTful endpoint for insights generation

### Streamlit Dashboard
- Interactive product visualizations
- Stock level alerts
- Price vs. stock analysis
- Delivery time monitoring

## ⚙️ Installation

Clone the repository:
```bash
git clone https://github.com/haf0g/hackai.git
cd retail-insight-assistant
```

Set up Python environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
Install dependencies:

```bash
pip install -r requirements.txt
```
 Usage
1. Start Flask API
```bash
export GROQ_API_KEY="your_groq_api_key_here"
python api_server.py
```
API will run at http://localhost:8501

2. Run Telegram Bot
Edit bot.py to add your bot token, then:

```bash
python bot.py
```
3. Launch Streamlit App
```bash
export GROQ_API_KEY="your_groq_api_key_here"
streamlit run app_streamlit.py
```
App will be available at http://localhost:8501

📊 Sample knowledge_base.json
json
{
  "products": [
    {
      "nom_article": "Lait entier",
      "societe_fabricant": "Danone",
      "prix": 1.20,
      "stock": 45,
      "description_produit": "Lait UHT entier 1L",
      "delai_livraison_moyen": "2 jours"
    },
    {
      "nom_article": "Pâtes spaghetti",
      "societe_fabricant": "Barilla",
      "prix": 1.50,
      "stock": 8,
      "description_produit": "Pâtes de qualité supérieure 500g",
      "delai_livraison_moyen": "5 jours"
    }
  ]
}
🔧 Requirements
The requirements.txt file should contain:
```
telegram==20.3
requests==2.31.0
flask==3.0.2
sentence-transformers==2.2.2
scikit-learn==1.4.0
streamlit==1.32.0
pandas==2.1.4
altair==5.2.0
groq==0.3.0
python-dotenv==1.0.0
```
🌐 Architecture

![alt text](deepseek_mermaid_20250525_0bd843.png)


Tips & Troubleshooting
- Common Issues
- Dependency conflicts: Use the exact versions in requirements.txt
- Groq API errors: Verify your API key and internet connection
- JSON loading issues: Validate your knowledge_base.json format



 Support
For assistance, please open an issue on GitHub or contact:
[garhoum.ensa@uhp.ac.ma]

License
MIT License
