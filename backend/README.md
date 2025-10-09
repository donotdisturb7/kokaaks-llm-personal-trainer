# Backend - KovaaK's AI Personal Trainer

Backend FastAPI pour l'assistant IA d'entraînement de visée avec connexion modulaire à Ollama.

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Copiez le fichier d'exemple et configurez vos paramètres :

```bash
cp env.example .env
```

Éditez le fichier `.env` pour configurer :

```env
# Configuration Ollama - modulaire pour localhost ou IP
OLLAMA_HOST=localhost          # ou une IP distante
OLLAMA_PORT=11434
OLLAMA_MODEL=llama2           # ou votre modèle préféré
OLLAMA_TIMEOUT=30

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

### 3. Test de connexion Ollama

```bash
python test_ollama.py
```

### 4. Démarrage de l'API

```bash
python run.py
```

L'API sera accessible sur : http://localhost:8000
Documentation : http://localhost:8000/docs

## 🔧 Configuration Ollama

### Connexion locale
```env
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

### Connexion distante
```env
OLLAMA_HOST=192.168.1.100    # IP de votre serveur Ollama
OLLAMA_PORT=11434
```

## 📡 Endpoints API

### Chat avec l'IA
- `POST /api/chat/message` - Envoyer un message
- `POST /api/chat/conversation` - Conversation complète
- `GET /api/chat/health` - Vérifier la connexion Ollama
- `GET /api/chat/models` - Lister les modèles disponibles

### Santé de l'API
- `GET /health` - Statut de l'API
- `GET /` - Informations générales

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── config.py            # Configuration et variables d'env
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py          # Routes pour le chat
│   └── services/
│       ├── __init__.py
│       └── ollama_service.py # Service Ollama modulaire
├── requirements.txt
├── env.example
├── run.py                   # Script de lancement
├── test_ollama.py          # Test de connexion
└── README.md
```

## 🔍 Fonctionnalités

- ✅ Connexion modulaire Ollama (localhost/IP)
- ✅ API REST avec FastAPI
- ✅ Gestion des erreurs
- ✅ Logging configuré
- ✅ CORS configuré
- ✅ Documentation automatique
- ✅ Tests de connexion
- ✅ Conseils spécialisés aim training

## 🐛 Dépannage

### Ollama non accessible
1. Vérifiez qu'Ollama est démarré : `ollama serve`
2. Vérifiez la configuration dans `.env`
3. Testez la connexion : `python test_ollama.py`

### Modèle non trouvé
1. Téléchargez un modèle : `ollama pull llama2`
2. Vérifiez les modèles disponibles : `ollama list`

### Erreurs de connexion
1. Vérifiez le firewall
2. Vérifiez l'IP et le port
3. Testez avec curl : `curl http://localhost:11434/api/tags`
