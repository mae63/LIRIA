# 🚀 LIRIA - Démarrage rapide avec Streamlit

## Installation locale

```bash
# Installer les dépendances Streamlit
pip install -r requirements-streamlit.txt

# Lancer l'application
streamlit run app.py
```

L'application sera accessible sur **http://localhost:8501**

## Démarrage du backend (optionnel)

Si tu veux utiliser le backend pour le chat et les recommandations intelligentes :

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Le backend sera accessible sur **http://localhost:8000**

## Déploiement public (Streamlit Cloud)

1. **Pousser ton code sur GitHub**
2. **Aller sur [share.streamlit.io](https://share.streamlit.io)**
3. **Connecter ton repository GitHub**
4. **Configurer** :
   - Main file: `app.py`
   - Python version: 3.9+
5. **Déployer !**

Tu auras une URL publique du type : `https://ton-app.streamlit.app`

## Configuration

### Variables d'environnement (optionnel)

Si tu déploies sur Streamlit Cloud, ajoute dans "Secrets" :

```toml
BACKEND_URL = "https://ton-backend.herokuapp.com"
STREAMLIT_CLOUD = "true"
```

### Sans backend

L'application fonctionne aussi sans backend :
- **Chat** : Nécessite le backend (ou désactiver cette fonctionnalité)
- **Search** : Fonctionne directement avec Google Books + OpenLibrary
- **Library** : Stockage local dans la session Streamlit

## Fonctionnalités

✅ **Chat avec LIRIA** - Recommandations intelligentes via LLM  
✅ **Recherche de livres** - Google Books + OpenLibrary  
✅ **Bibliothèque personnelle** - Ajout, notation, commentaires  
✅ **Interface moderne** - Design épuré avec Streamlit

## Notes

- La bibliothèque est stockée dans la session Streamlit (se réinitialise à chaque redémarrage)
- Pour la persistance, tu peux ajouter une base de données (SQLite, PostgreSQL, etc.)
- Le backend est optionnel : la recherche fonctionne sans lui

