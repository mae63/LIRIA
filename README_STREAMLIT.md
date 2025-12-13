# 🚀 LIRIA - Guide de démarrage

## 📋 Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

## 🎯 Démarrage rapide

### 1. Installation des dépendances

```bash
# Installer les dépendances pour Streamlit
pip install -r requirements-streamlit.txt
```

### 2. Configuration du backend (optionnel mais recommandé pour le chat)

Le backend est nécessaire pour la fonctionnalité de chat avec LIRIA. Pour le configurer :

1. **Créer le fichier `.env` dans le dossier `backend/`** :
   ```bash
   cd backend
   ```

2. **Ajouter tes clés API dans `backend/.env`** :
   ```env
   GEMINI_API_KEY=ta_cle_gemini_ici
   LLM_PROVIDER=gemini
   GEMINI_MODEL=gemini-2.5-pro
   USE_GOOGLE_BOOKS=true
   ```

3. **Installer les dépendances du backend** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Démarrer le backend** :
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Le backend sera accessible sur **http://localhost:8000**

### 3. Lancer l'application Streamlit

Dans le dossier racine du projet :

```bash
# Si tu es dans backend/, retourne au dossier racine
cd ..

# Lancer Streamlit
python -m streamlit run app.py
```

L'application sera accessible sur **http://localhost:8501**

## 🌐 Déploiement public (Streamlit Cloud)

### Étapes de déploiement

1. **Pousser ton code sur GitHub** (si ce n'est pas déjà fait)
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Aller sur [share.streamlit.io](https://share.streamlit.io)**
   - Connecte-toi avec ton compte GitHub
   - Clique sur "New app"

3. **Configurer l'application** :
   - **Repository** : Sélectionne ton repo GitHub
   - **Branch** : `main` (ou la branche principale)
   - **Main file path** : `app.py`
   - **Python version** : 3.9 ou supérieur

4. **Configurer les secrets** (pour le backend) :
   - Clique sur "Advanced settings"
   - Dans "Secrets", ajoute :
   ```toml
   BACKEND_URL = "https://ton-backend-url.com"
   STREAMLIT_CLOUD = "true"
   GEMINI_API_KEY = "ta_cle_gemini"
   ```

5. **Déployer !**
   - Clique sur "Deploy"
   - Attends quelques minutes
   - Tu auras une URL publique du type : `https://ton-app.streamlit.app`

## 🎨 Fonctionnalités

### ✅ Chat avec LIRIA
- Recommandations intelligentes basées sur tes préférences
- Nécessite le backend avec clé Gemini API
- Interface conversationnelle naturelle

### ✅ Recherche de livres
- Recherche en temps réel via Google Books et OpenLibrary
- Fonctionne **sans backend** (appels API directs)
- Affichage des descriptions, couvertures, et catégories

### ✅ Bibliothèque personnelle
- Ajout de livres depuis le chat ou la recherche
- Système de notation par étoiles (1-5)
- Commentaires personnels
- Affichage des notes communautaires

### ✅ Interface moderne
- Thème sombre élégant
- Design responsive
- Navigation intuitive

## ⚙️ Configuration

### Variables d'environnement

#### Pour le backend (`backend/.env`) :
```env
GEMINI_API_KEY=ta_cle_gemini
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-pro
EMBEDDING_PROVIDER=gemini
USE_GOOGLE_BOOKS=true
```

#### Pour Streamlit Cloud (dans "Secrets") :
```toml
BACKEND_URL = "https://ton-backend.herokuapp.com"
STREAMLIT_CLOUD = "true"
```

### Sans backend

L'application fonctionne partiellement sans backend :
- ✅ **Search** : Fonctionne directement
- ✅ **Library** : Stockage local (session Streamlit)
- ❌ **Chat** : Nécessite le backend

## 📝 Notes importantes

- **Bibliothèque** : Stockée dans la session Streamlit (se réinitialise à chaque redémarrage de l'app)
- **Backend** : Optionnel pour la recherche, **requis** pour le chat
- **Clés API** : Google Books et OpenLibrary fonctionnent sans clé API (limites de taux appliquées)

## 🐛 Dépannage

### Le chat ne fonctionne pas
- Vérifie que le backend est démarré : `http://localhost:8000/health`
- Vérifie ta clé Gemini dans `backend/.env`
- Consulte les logs du backend pour les erreurs

### La recherche ne retourne aucun résultat
- Vérifie ta connexion internet
- Les APIs Google Books et OpenLibrary peuvent avoir des limites de taux
- Essaie une recherche différente

### L'application ne se lance pas
- Vérifie que toutes les dépendances sont installées : `pip install -r requirements-streamlit.txt`
- Vérifie ta version de Python : `python --version` (doit être 3.9+)

## 📚 Structure du projet

```
.
├── app.py                      # Application Streamlit principale
├── requirements-streamlit.txt  # Dépendances Streamlit
├── .streamlit/
│   └── config.toml            # Configuration Streamlit (thème sombre)
├── backend/
│   ├── main.py                # API FastAPI
│   ├── requirements.txt       # Dépendances backend
│   └── .env                   # Clés API (à créer)
└── README_STREAMLIT.md        # Ce fichier
```

## 🚀 Commandes rapides

```bash
# Démarrer le backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Démarrer Streamlit (dans un autre terminal)
python -m streamlit run app.py

# Vérifier que le backend fonctionne
curl http://localhost:8000/health
```

---

**Bon développement ! 📚✨**
