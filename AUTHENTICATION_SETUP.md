# LIRIA Authentication & Database Setup

This guide explains how to set up user authentication and persistent storage for LIRIA using Supabase.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. A Supabase project created

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Create a new project
3. Note down your project URL and anon key (found in Settings > API)

## Step 2: Set Up Database Schema

1. In your Supabase project, go to the SQL Editor
2. Copy and paste the contents of `backend/supabase_schema.sql`
3. Run the SQL script to create all necessary tables and policies

## Step 3: Configure Environment Variables

### Backend (.env file in `backend/` directory)

**C'est le seul fichier .env nécessaire pour commencer !**

Create a `.env` file in the `backend/` directory with:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

Remplacez `your-project-id`, `your-anon-key-here` et `your-service-role-key-here` par les valeurs de votre projet Supabase.

**Note importante :**
- `SUPABASE_ANON_KEY` : Trouvable dans Settings > API > anon/public key
- `SUPABASE_SERVICE_ROLE_KEY` : Trouvable dans Settings > API > service_role key (⚠️ **NE JAMAIS EXPOSER CETTE CLÉ** - elle donne un accès admin complet)
- La `SERVICE_ROLE_KEY` est utilisée pour auto-confirmer les emails lors de l'inscription (optionnel mais recommandé pour le développement)

### Frontend (.env file - OPTIONNEL)

**Note:** Le fichier `.env` à la racine n'est **pas obligatoire** si votre backend tourne sur `http://localhost:8000` (valeur par défaut).

Vous n'avez besoin d'un fichier `.env` à la racine **que si** :
- Votre backend tourne sur un autre port (ex: `http://localhost:8001`)
- Votre backend est déployé sur un serveur distant (ex: `https://api.votre-domaine.com`)

Dans ce cas, créez un fichier `.env` à la racine du projet :

```env
BACKEND_URL=http://localhost:8000
```

Pour la production, mettez à jour `BACKEND_URL` avec l'URL de votre API backend.

## Step 4: Install Dependencies

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

The frontend uses Streamlit, which should already be installed. If not:

```bash
pip install streamlit requests
```

## Step 5: Run the Application

### Start Backend

```bash
cd backend
uvicorn main:app --reload
```

### Start Frontend

```bash
streamlit run app.py
```

## Features

### Authentication

- **Sign Up**: Users can create accounts with email and password
- **Sign In**: Existing users can log in
- **Sign Out**: Users can log out
- **Session Management**: Access tokens are stored in session state

### Data Persistence

All user data is stored in Supabase:

- **Library**: Books users have read, with ratings and comments
- **Wishlist**: Books saved from recommendations
- **Conversations**: Chat history is saved and restored on login
- **Messages**: Individual messages are stored per conversation

### Data Migration

When a user first logs in, any existing localStorage data (if present) is automatically migrated to the database.

## Database Schema

- `library_entries`: User's reading library
- `wishlist_entries`: Saved book recommendations
- `conversations`: Chat conversation records
- `messages`: Individual chat messages

All tables use Row Level Security (RLS) to ensure users can only access their own data.

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/signin` - Sign in
- `POST /auth/signout` - Sign out

### Library
- `GET /library` - Get user's library
- `POST /library` - Add book to library
- `PUT /library/{entry_id}` - Update library entry
- `DELETE /library/{entry_id}` - Delete library entry

### Wishlist
- `GET /wishlist` - Get user's wishlist
- `POST /wishlist` - Add book to wishlist
- `DELETE /wishlist/{entry_id}` - Remove from wishlist

### Conversations
- `GET /conversations/latest` - Get latest conversation with messages
- `POST /conversations` - Create new conversation
- `POST /conversations/{conversation_id}/messages` - Add message

### Migration
- `POST /migrate/localstorage` - Migrate localStorage data to database

## Troubleshooting

### "Authentication not configured" error

Make sure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set in your backend `.env` file.

### "Database not configured" error

Check that:
1. The SQL schema has been run in Supabase
2. RLS policies are enabled
3. Environment variables are correct

### Data not persisting

1. Check that you're logged in (authentication is required)
2. Verify your Supabase project is active
3. Check browser console and backend logs for errors

## Security Notes

- Access tokens are stored in Streamlit session state (server-side)
- All API endpoints require authentication via Bearer token
- Row Level Security ensures users can only access their own data
- Passwords are hashed by Supabase Auth

