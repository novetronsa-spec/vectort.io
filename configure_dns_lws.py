#!/usr/bin/env python3
"""
Script de configuration automatique DNS LWS pour vectort.io
Configure les enregistrements A pour le domaine et sous-domaines
"""

import requests
import sys
import time

# Configuration
API_KEY = "3zDaUP2mnBQih1ZyWCYOq9dFgL7wcEltSX4s8kMfAxNoTeJrbH"
DOMAIN = "vectort.io"
SERVER_IP = "156.67.26.106"
SERVER_IPV6 = "2a02:c207:2285:5086::1"
API_BASE_URL = "https://api.lws.net/v1"

# Headers pour l'API
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_dns_record(name, record_type, data, ttl=3600):
    """
    Crée un enregistrement DNS via l'API LWS
    
    Args:
        name: Nom de l'enregistrement (@ pour root, www, api, etc.)
        record_type: Type d'enregistrement (A, AAAA, CNAME, etc.)
        data: Valeur de l'enregistrement (IP, domaine, etc.)
        ttl: Time to live en secondes
    """
    url = f"{API_BASE_URL}/domain/{DOMAIN}/zdns"
    
    payload = {
        "name": name if name != "@" else "",
        "type": record_type,
        "data": data,
        "ttl": ttl
    }
    
    print(f"📝 Création de l'enregistrement {record_type} : {name} -> {data}")
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=30)
        
        if response.status_code in [200, 201]:
            print(f"✅ Enregistrement {name} créé avec succès !")
            return True
        elif response.status_code == 409:
            print(f"⚠️  Enregistrement {name} existe déjà (normal)")
            return True
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à l'API LWS: {e}")
        return False

def get_existing_records():
    """Récupère les enregistrements DNS existants"""
    url = f"{API_BASE_URL}/domain/{DOMAIN}/zdns"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Impossible de récupérer les enregistrements existants")
            return None
    except Exception as e:
        print(f"⚠️  Erreur lors de la récupération des enregistrements: {e}")
        return None

def main():
    print("🚀 Configuration automatique du DNS pour vectort.io")
    print("=" * 60)
    print(f"Domaine: {DOMAIN}")
    print(f"IP Serveur: {SERVER_IP}")
    print(f"IPv6 Serveur: {SERVER_IPV6}")
    print("=" * 60)
    print()
    
    # Vérifier les enregistrements existants
    print("🔍 Vérification des enregistrements existants...")
    existing = get_existing_records()
    if existing:
        print(f"📋 {len(existing)} enregistrement(s) existant(s)")
    print()
    
    # Liste des enregistrements à créer
    records = [
        # Enregistrements A (IPv4)
        ("@", "A", SERVER_IP, "Domaine principal"),
        ("www", "A", SERVER_IP, "Sous-domaine www"),
        ("api", "A", SERVER_IP, "API backend"),
        
        # Enregistrements AAAA (IPv6)
        ("@", "AAAA", SERVER_IPV6, "IPv6 domaine principal"),
    ]
    
    success_count = 0
    total = len(records)
    
    for name, record_type, data, description in records:
        print(f"\n📌 {description}")
        if create_dns_record(name, record_type, data):
            success_count += 1
        time.sleep(1)  # Pause entre les requêtes pour éviter rate limiting
    
    print()
    print("=" * 60)
    print(f"✅ Configuration terminée : {success_count}/{total} enregistrements configurés")
    print("=" * 60)
    print()
    
    if success_count == total:
        print("🎉 SUCCÈS ! Tous les enregistrements DNS ont été configurés.")
        print()
        print("⏱️  Propagation DNS en cours...")
        print("   - Généralement : 10-30 minutes")
        print("   - Maximum : 24-48 heures")
        print()
        print("🔍 Vérifiez la propagation avec :")
        print(f"   ping {DOMAIN}")
        print(f"   nslookup {DOMAIN}")
        print()
        print("🚀 Une fois le DNS propagé, lancez le déploiement :")
        print(f"   ssh root@{SERVER_IP}")
        print("   cd /opt/vectort")
        print("   ./deploy.sh")
        return 0
    else:
        print("⚠️  Certains enregistrements n'ont pas pu être créés.")
        print("   Vérifiez manuellement sur https://www.lws.fr")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Annulé par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
