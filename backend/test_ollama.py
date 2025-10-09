#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion Ollama
Teste la connectivité et les fonctionnalités de base
"""
import asyncio
import sys
import os

# Ajouter le dossier app au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import get_settings
from app.services.ollama_service import create_ollama_service


async def test_ollama_connection():
    """Test de connexion à Ollama"""
    print("🔍 Test de connexion Ollama...")
    print("=" * 50)
    
    settings = get_settings()
    print(f"📍 Configuration Ollama:")
    print(f"   Host: {settings.ollama_host}")
    print(f"   Port: {settings.ollama_port}")
    print(f"   Modèle: {settings.ollama_model}")
    print(f"   URL: {settings.ollama_base_url}")
    print()
    
    try:
        async with create_ollama_service(settings) as ollama:
            # Test 1: Health check
            print("1️⃣ Test de santé (health check)...")
            is_healthy = await ollama.health_check()
            if is_healthy:
                print("   ✅ Ollama est accessible")
            else:
                print("   ❌ Ollama n'est pas accessible")
                return False
            print()
            
            # Test 2: Liste des modèles
            print("2️⃣ Récupération des modèles disponibles...")
            models = await ollama.get_available_models()
            if models:
                print(f"   ✅ {len(models)} modèle(s) trouvé(s):")
                for model in models:
                    print(f"      - {model}")
            else:
                print("   ⚠️  Aucun modèle trouvé")
            print()
            
            # Test 3: Génération de texte simple
            print("3️⃣ Test de génération de texte...")
            test_prompt = "Dis bonjour en français"
            response = await ollama.generate_response(test_prompt)
            if response:
                print(f"   ✅ Réponse générée:")
                print(f"      Prompt: {test_prompt}")
                print(f"      Réponse: {response[:100]}...")
            else:
                print("   ❌ Aucune réponse générée")
            print()
            
            # Test 4: Génération spécialisée aim training
            print("4️⃣ Test de génération spécialisée (aim training)...")
            aim_prompt = "Comment améliorer mon tracking dans KovaaK's ?"
            aim_response = await ollama.generate_aim_training_advice(aim_prompt)
            if aim_response:
                print(f"   ✅ Conseil d'entraînement généré:")
                print(f"      Question: {aim_prompt}")
                print(f"      Réponse: {aim_response[:150]}...")
            else:
                print("   ❌ Aucun conseil généré")
            print()
            
            print("🎉 Tous les tests sont passés avec succès !")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False


async def main():
    """Fonction principale"""
    print("🤖 Test de connexion Ollama pour KovaaK's AI Personal Trainer")
    print("=" * 70)
    print()
    
    success = await test_ollama_connection()
    
    print()
    print("=" * 70)
    if success:
        print("✅ Connexion Ollama fonctionnelle !")
        print("🚀 Vous pouvez maintenant démarrer l'API avec: python run.py")
    else:
        print("❌ Problème de connexion Ollama")
        print("💡 Vérifiez que:")
        print("   - Ollama est installé et démarré")
        print("   - Le modèle est téléchargé")
        print("   - Les paramètres de connexion sont corrects")
        print("   - Le fichier .env est configuré")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
