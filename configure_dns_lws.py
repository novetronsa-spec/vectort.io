#!/usr/bin/env python3
"""
Script de configuration automatique DNS LWS pour vectort.io
Configure les enregistrements A pour le domaine et sous-domaines
"""

import requests
import sys
import time

# Configuration
API_KEY = "zvPaiA9UKOXJTFoeHEqCsDSlWw2fR8un6Q3VZYkN75t0hmBbyM"
LOGIN = "amoa.j.aymar@gmail.com"
PASSWORD = "@@aaEE7610"
DOMAIN = "vectort.io"
SERVER_IP = "31.165.143.145"
SERVER_IPV6 = "2a02:c207:2285:5086::1"
API_BASE_URL = "https://api.lws.net/v1"

# Headers pour l'API avec authentification complète
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "X-Auth-Login": LOGIN,
    "X-Auth-Pass": PASSWORD,
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
            print(f"⚠️  Enregistrement {name} existe déjà, mise à jour...")
            # Tenter de mettre à jour l'enregistrement existant
            return update_dns_record(name, record_type, data, ttl)
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion à l'API LWS: {e}")
        return False

def update_dns_record(name, record_type, data, ttl=3600):
    """Met à jour un enregistrement DNS existant"""
    url = f"{API_BASE_URL}/domain/{DOMAIN}/zdns"
    
    # D'abord, récupérer l'ID de l'enregistrement
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            records = response.json()
            # Chercher l'enregistrement correspondant
            for record in records:
                if record.get('name') == (name if name != "@" else "") and record.get('type') == record_type:
                    record_id = record.get('id')
                    # Mettre à jour
                    update_url = f"{url}/{record_id}"
                    payload = {"data": data, "ttl": ttl}
                    update_response = requests.put(update_url, json=payload, headers=HEADERS, timeout=30)
                    if update_response.status_code in [200, 204]:
                        print(f"✅ Enregistrement {name} mis à jour !")
                        return True
        return False
    except Exception as e:
        print(f"⚠️  Impossible de mettre à jour: {e}")
        return False

def get_existing_records():
    """Récupère les enregistrements DNS existants"""
    url = f"{API_BASE_URL}/domain/{DOMAIN}/zdns"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Impossible de récupérer les enregistrements existants: {response.text}")
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
    print(f"Compte LWS: {LOGIN}")
    print("=" * 60)
    print()
    
    # Vérifier les enregistrements existants
    print("🔍 Vérification des enregistrements existants...")
    existing = get_existing_records()
    if existing:
        print(f"📋 {len(existing)} enregistrement(s) existant(s)")
        for record in existing:
            print(f"   - {record.get('type')} : {record.get('name') or '@'} → {record.get('data')}")
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
    
    if success_count >= total - 1:  # Au moins 3/4 réussis
        print("🎉 SUCCÈS ! Les enregistrements DNS ont été configurés.")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
