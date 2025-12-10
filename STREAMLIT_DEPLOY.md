# Déploiement de LIRIA avec Streamlit

Ce guide explique comment déployer LIRIA sur Streamlit Cloud pour avoir une URL publique accessible.

## 🚀 Déploiement rapide

### Option 1 : Streamlit Cloud (Recommandé - Gratuit)

1. **Préparer le repository**
   - Assure-toi que ton code est sur GitHub (public ou privé)
   - Le fichier `app.py` doit être à la racine du repository

2. **Créer un compte Streamlit Cloud**
   - Va sur [share.streamlit.io](https://share.streamlit.io)
   - Connecte-toi avec ton compte GitHub

3. **Déployer l'application**
   - Clique sur "New app"
   - Sélectionne ton repository
   - **Main file path**: `app.py`
   - **Python version**: 3.9 ou supérieur
   - Clique sur "Deploy"

4. **Configurer les secrets (optionnel)**
   - Dans l'interface Streamlit Cloud, va dans "Settings" > "Secrets"
   - Ajoute les variables d'environnement :
     ```toml
     BACKEND_URL = "https://ton-backend-url.herokuapp.com"
     STREAMLIT_CLOUD = "true"
     ```

### Option 2 : Déploiement local

```bash
# Installer Streamlit
pip install -r requirements-streamlit.txt

# Lancer l'application
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📋 Configuration

### Variables d'environnement

- `BACKEND_URL`: URL du backend FastAPI (par défaut: `http://localhost:8000`)
- `STREAMLIT_CLOUD`: `"true"` si déployé sur Streamlit Cloud

### Fichiers de configuration

- `.streamlit/config.toml`: Configuration de l'apparence
- `.streamlit/secrets.toml`: Secrets locaux (ne pas commiter)

## 🔧 Déploiement du backend

Pour que l'application fonctionne complètement, tu dois aussi déployer le backend FastAPI.

### Option 1 : Heroku (Gratuit)

1. Créer un compte Heroku
2. Installer Heroku CLI
3. Dans le dossier `backend/`:
   ```bash
   heroku create ton-app-name
   git push heroku main
   ```
4. Configurer les variables d'environnement dans Heroku Dashboard:
   - `GEMINI_API_KEY`
   - `GOOGLE_BOOKS_API_KEY` (optionnel)
   - `USE_GOOGLE_BOOKS=true`

### Option 2 : Railway (Gratuit)

1. Créer un compte Railway
2. Connecter ton repository GitHub
3. Sélectionner le dossier `backend/`
4. Railway détectera automatiquement FastAPI
5. Ajouter les variables d'environnement dans Railway

### Option 3 : Render (Gratuit)

1. Créer un compte Render
2. Créer un nouveau "Web Service"
3. Connecter ton repository
4. Configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Ajouter les variables d'environnement

## 🌐 URLs publiques

Une fois déployé:
- **Streamlit Frontend**: `https://ton-app.streamlit.app`
- **Backend API**: `https://ton-backend.herokuapp.com` (ou autre)

## ⚠️ Notes importantes

1. **CORS**: Le backend est configuré pour accepter toutes les origines (`allow_origins=["*"]`)

2. **Secrets**: Ne jamais commiter les clés API. Utilise les secrets de Streamlit Cloud/Heroku

3. **Backend URL**: Si le backend n'est pas accessible, l'application utilisera la recherche directe (Google Books + OpenLibrary) comme fallback

4. **Performance**: Streamlit Cloud offre un plan gratuit avec des limitations. Pour plus de ressources, considère un plan payant.

## 🐛 Dépannage

### L'application ne se connecte pas au backend
- Vérifie que `BACKEND_URL` est correctement configuré
- Vérifie que le backend est bien déployé et accessible
- Active le fallback en décochant "Use backend API" dans la page Search

### Erreur de CORS
- Vérifie que le backend accepte toutes les origines (déjà configuré)
- Vérifie les logs du backend

### L'application est lente
- Streamlit Cloud peut être lent sur le plan gratuit
- Considère utiliser la recherche directe au lieu du backend pour la page Search

