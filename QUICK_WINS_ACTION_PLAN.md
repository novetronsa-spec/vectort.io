# ⚡ Vectort.io - Plan d'Action Immédiat (Quick Wins)

## 🎯 Objectif: Implémenter les améliorations critiques en 2 semaines

---

## 📅 SEMAINE 1: Performance & Cache

### Jour 1-2: Cache LRU In-Memory ✅ PRIORITÉ MAX

**Problème actuel:** Chaque génération appelle le LLM (coût $0.02-0.10)
**Solution:** Cache en mémoire pour prompts similaires

**Implémentation:**

```python
# Ajouter à /app/backend/server.py

from functools import lru_cache
import hashlib
import json

def generate_cache_key(description: str, framework: str, type: str) -> str:
    """Generate unique cache key for AI generation"""
    data = {
        "description": description.lower().strip(),
        "framework": framework,
        "type": type
    }
    key_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(key_string.encode()).hexdigest()

# Cache pour 1000 dernières générations
@lru_cache(maxsize=1000)
def get_cached_code(cache_key: str):
    """Get code from database cache"""
    cached = db.generated_apps.find_one(
        {"cache_key": cache_key},
        sort=[("created_at", -1)]
    )
    return cached

# Modifier la route de génération
@api_router.post("/projects/{project_id}/generate")
async def generate_code_with_cache(...):
    # Generate cache key
    cache_key = generate_cache_key(
        request.description,
        request.framework,
        request.type
    )
    
    # Check cache first
    cached_result = get_cached_code(cache_key)
    if cached_result and not request.force_regenerate:
        logger.info(f"Cache hit for key: {cache_key}")
        return GeneratedApp(**cached_result)
    
    # Generate with AI if not cached
    logger.info(f"Cache miss, generating with AI: {cache_key}")
    result = await generate_with_ai(request)
    
    # Save with cache key
    result_dict = result.dict()
    result_dict["cache_key"] = cache_key
    await db.generated_apps.insert_one(result_dict)
    
    return result
```

**Bénéfices attendus:**
- ✅ Réduction coûts LLM: 30-40%
- ✅ Latence: 15s → 0.5s (cache hit)
- ✅ Pas d'infrastructure additionnelle

**Testing:**
```bash
# Test 1: Générer un projet
curl -X POST /api/projects/123/generate -d '{"description": "todo app"}'

# Test 2: Même projet (devrait être instantané)
curl -X POST /api/projects/123/generate -d '{"description": "todo app"}'
```

---

### Jour 3-4: Rate Limiting ✅ SÉCURITÉ

**Problème:** Pas de protection contre abus API
**Solution:** Limiter les requêtes par user/IP

**Implémentation:**

```python
# Ajouter à requirements.txt
slowapi==0.1.9

# Ajouter à server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Appliquer aux routes sensibles
@api_router.post("/projects/{project_id}/generate")
@limiter.limit("10/minute")  # 10 générations max par minute
async def generate_code(...):
    ...

@api_router.post("/auth/register")
@limiter.limit("5/hour")  # 5 inscriptions max par heure
async def register(...):
    ...

@api_router.post("/credits/purchase")
@limiter.limit("20/hour")  # Protection achat
async def purchase_credits(...):
    ...
```

**Configuration par plan:**
```python
RATE_LIMITS = {
    "free": "10/minute",
    "starter": "30/minute",
    "pro": "100/minute",
    "enterprise": "unlimited"
}

# Dynamic rate limiting
@limiter.limit(lambda: RATE_LIMITS[current_user.subscription_plan])
async def generate_code(...):
    ...
```

---

### Jour 5: Monitoring Basique ✅ OBSERVABILITÉ

**Problème:** Aucune visibilité sur les erreurs en production
**Solution:** Sentry.io pour error tracking

**Implémentation:**

```python
# Ajouter à requirements.txt
sentry-sdk[fastapi]==1.40.0

# Ajouter à server.py (au début)
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
    traces_sample_rate=0.1,  # 10% des requêtes
    profiles_sample_rate=0.1,
    environment=os.environ.get('ENV', 'production'),
    release=f"vectort@{os.environ.get('VERSION', '1.0.0')}"
)

# Contexte utilisateur
@app.middleware("http")
async def add_sentry_context(request: Request, call_next):
    user = getattr(request.state, "user", None)
    if user:
        sentry_sdk.set_user({
            "id": user.id,
            "email": user.email,
            "username": user.full_name
        })
    response = await call_next(request)
    return response

# Custom events
def track_generation_failure(error: Exception, project_id: str):
    sentry_sdk.capture_exception(
        error,
        extras={
            "project_id": project_id,
            "error_type": type(error).__name__
        }
    )
```

**Setup Sentry:**
1. Créer compte sur sentry.io (gratuit jusqu'à 5K events/mois)
2. Copier le DSN
3. Ajouter à .env: `SENTRY_DSN=https://xxx@sentry.io/yyy`

---

## 📅 SEMAINE 2: Logs & Storage

### Jour 6-7: Logging Structuré ✅ DEBUGGING

**Problème:** Logs désorganisés, difficiles à filtrer
**Solution:** JSON structured logging

**Implémentation:**

```python
# Ajouter à requirements.txt
python-json-logger==2.0.7

# Créer /app/backend/utils/logger.py
import logging
from pythonjsonlogger import jsonlogger

def setup_logger():
    logger = logging.getLogger()
    
    # Handler avec format JSON
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger

# Usage dans server.py
from utils.logger import setup_logger

logger = setup_logger()

# Log structured data
logger.info(
    "generation_started",
    extra={
        "user_id": user.id,
        "project_id": project_id,
        "framework": request.framework,
        "model": "gpt-5"
    }
)

logger.info(
    "generation_completed",
    extra={
        "user_id": user.id,
        "project_id": project_id,
        "duration_seconds": duration,
        "code_length": len(generated_code),
        "cost_usd": estimated_cost
    }
)

logger.error(
    "generation_failed",
    extra={
        "user_id": user.id,
        "project_id": project_id,
        "error": str(e),
        "provider": "gpt-5"
    },
    exc_info=True
)
```

**Analyse des logs:**
```bash
# Filtrer par user
cat backend.log | jq 'select(.user_id == "abc123")'

# Toutes les erreurs LLM
cat backend.log | jq 'select(.levelname == "ERROR" and .message == "generation_failed")'

# Coût total journalier
cat backend.log | jq -s 'map(select(.message == "generation_completed")) | map(.cost_usd) | add'
```

---

### Jour 8-9: S3 File Storage ✅ SCALABILITÉ

**Problème:** Fichiers ZIP stockés en DB (limite MongoDB 16MB)
**Solution:** AWS S3 pour storage scalable

**Implémentation:**

```python
# Ajouter à requirements.txt
boto3==1.34.60

# Créer /app/backend/utils/s3_storage.py
import boto3
import os
from datetime import datetime, timedelta

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.environ.get('S3_BUCKET_NAME', 'vectort-generated-code')
    
    def upload_project_zip(self, project_id: str, user_id: str, zip_data: bytes) -> str:
        """Upload project ZIP to S3"""
        key = f"users/{user_id}/projects/{project_id}/code.zip"
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=zip_data,
            ContentType='application/zip',
            Metadata={
                'project_id': project_id,
                'user_id': user_id,
                'generated_at': datetime.utcnow().isoformat()
            }
        )
        
        return key
    
    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate presigned URL for download (expires in 1h)"""
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expires_in
        )
        return url
    
    def delete_project_files(self, user_id: str, project_id: str):
        """Delete all files for a project"""
        prefix = f"users/{user_id}/projects/{project_id}/"
        
        objects = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix
        )
        
        if 'Contents' in objects:
            delete_keys = [{'Key': obj['Key']} for obj in objects['Contents']]
            self.s3.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': delete_keys}
            )

s3_storage = S3Storage()

# Usage dans export routes
@api_router.post("/projects/{project_id}/export/zip")
async def export_to_zip_s3(project_id: str, current_user: User = Depends(get_current_user)):
    # Generate ZIP
    zip_data = await generate_project_zip(project_id)
    
    # Upload to S3
    s3_key = s3_storage.upload_project_zip(
        project_id=project_id,
        user_id=current_user.id,
        zip_data=zip_data
    )
    
    # Generate download URL
    download_url = s3_storage.generate_download_url(s3_key, expires_in=86400)  # 24h
    
    return {
        "download_url": download_url,
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
```

**Configuration S3:**
```bash
# Ajouter à .env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=vectort-generated-code
```

**Création bucket S3:**
```bash
# Créer bucket
aws s3 mb s3://vectort-generated-code

# Configurer lifecycle policy (archive après 90 jours)
aws s3api put-bucket-lifecycle-configuration \
  --bucket vectort-generated-code \
  --lifecycle-configuration file://lifecycle.json
```

---

### Jour 10: Métriques Prometheus ✅ PERFORMANCE

**Problème:** Pas de métriques temps réel
**Solution:** Prometheus + Grafana

**Implémentation:**

```python
# Ajouter à requirements.txt
prometheus-client==0.19.0
prometheus-fastapi-instrumentator==6.1.0

# Ajouter à server.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
generation_counter = Counter(
    'vectort_generations_total',
    'Total number of code generations',
    ['status', 'model', 'framework']
)

generation_duration = Histogram(
    'vectort_generation_duration_seconds',
    'Time spent generating code',
    ['model', 'framework']
)

credits_balance = Gauge(
    'vectort_user_credits',
    'Current user credit balance',
    ['user_id']
)

llm_cost = Counter(
    'vectort_llm_cost_usd',
    'Total LLM API cost in USD',
    ['provider']
)

# Instrumenter FastAPI
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/api/metrics")

# Usage
@api_router.post("/projects/{project_id}/generate")
async def generate_code_with_metrics(...):
    start_time = time.time()
    
    try:
        result = await generate_with_ai(request)
        
        # Métriques de succès
        generation_counter.labels(
            status='success',
            model='gpt-5',
            framework=request.framework
        ).inc()
        
        duration = time.time() - start_time
        generation_duration.labels(
            model='gpt-5',
            framework=request.framework
        ).observe(duration)
        
        return result
        
    except Exception as e:
        generation_counter.labels(
            status='error',
            model='gpt-5',
            framework=request.framework
        ).inc()
        raise
```

**Dashboard Grafana:**
```yaml
# Panels suggérés
- Generations per minute (rate)
- Success rate (%)
- P95 generation latency
- LLM costs (cumulative)
- Active users (gauge)
- Credit consumption rate
```

---

## 🧪 Testing des Quick Wins

### Test Suite Complet

```python
# /app/backend/tests/test_quick_wins.py

import pytest
from fastapi.testclient import TestClient

def test_cache_works(client: TestClient):
    """Test que le cache fonctionne"""
    # Première requête
    response1 = client.post("/api/projects/123/generate", json={
        "description": "simple todo app",
        "framework": "react"
    })
    time1 = response1.elapsed.total_seconds()
    
    # Deuxième requête (devrait être cached)
    response2 = client.post("/api/projects/123/generate", json={
        "description": "simple todo app",
        "framework": "react"
    })
    time2 = response2.elapsed.total_seconds()
    
    assert response1.json() == response2.json()
    assert time2 < time1 * 0.5  # Cache devrait être 50%+ plus rapide

def test_rate_limiting(client: TestClient):
    """Test rate limiting"""
    # Faire 11 requêtes (limite = 10)
    responses = []
    for i in range(11):
        resp = client.post("/api/projects/123/generate", json={
            "description": f"app {i}"
        })
        responses.append(resp.status_code)
    
    # La 11ème devrait être rate limited
    assert responses[-1] == 429

def test_s3_upload(client: TestClient):
    """Test S3 storage"""
    response = client.post("/api/projects/123/export/zip")
    
    assert response.status_code == 200
    assert "download_url" in response.json()
    assert "s3.amazonaws.com" in response.json()["download_url"]
```

---

## 📊 Métriques de Succès

### KPIs à tracker après implémentation:

```
Cache:
✅ Cache hit rate: Target 30-50%
✅ Réduction coûts LLM: Target 40%
✅ Latence moyenne: < 2s (vs 15s avant)

Rate Limiting:
✅ Requêtes bloquées: < 1% des requêtes légitimes
✅ Abus détectés: Nombre de 429 errors

Monitoring:
✅ Erreurs détectées dans Sentry: 100%
✅ Temps de résolution bugs: -50%
✅ Alertes configurées: > 5

Storage:
✅ Uploads S3: 100% succès
✅ Coût storage: < $50/mois (début)
✅ Download speed: > 1MB/s
```

---

## 💰 Coût Additionnel Estimé

```
Sentry.io:        $0-26/mois (gratuit jusqu'à 5K events)
AWS S3:           $5-20/mois (premier TB = $0.023/GB)
Prometheus:       $0 (self-hosted)
Grafana Cloud:    $0-49/mois (gratuit jusqu'à 10K series)
slowapi:          $0 (open source)

Total:            $5-95/mois
ROI:              Économies LLM > $500/mois avec cache
```

---

## ✅ Checklist d'Implémentation

### Semaine 1
- [ ] Jour 1-2: Implémenter cache LRU
  - [ ] Fonction generate_cache_key
  - [ ] Modifier route /generate
  - [ ] Tester cache hit/miss
  - [ ] Mesurer économies

- [ ] Jour 3-4: Ajouter rate limiting
  - [ ] Installer slowapi
  - [ ] Configurer limites par route
  - [ ] Tester avec script
  - [ ] Documenter API limits

- [ ] Jour 5: Setup Sentry
  - [ ] Créer compte Sentry
  - [ ] Configurer DSN
  - [ ] Tester error tracking
  - [ ] Créer alertes

### Semaine 2
- [ ] Jour 6-7: Logging structuré
  - [ ] Installer python-json-logger
  - [ ] Créer utils/logger.py
  - [ ] Migrer tous les logs
  - [ ] Test log analysis

- [ ] Jour 8-9: S3 Storage
  - [ ] Créer bucket S3
  - [ ] Implémenter S3Storage class
  - [ ] Migrer export ZIP vers S3
  - [ ] Tester presigned URLs

- [ ] Jour 10: Prometheus metrics
  - [ ] Installer instrumentator
  - [ ] Ajouter custom metrics
  - [ ] Exposer /metrics endpoint
  - [ ] Créer dashboard Grafana

---

## 🚀 Déploiement

### Mise en production:

```bash
# 1. Backup database
mongodump --uri="$MONGO_URL" --out=/backup

# 2. Installer nouvelles dépendances
pip install -r requirements.txt

# 3. Ajouter variables d'environnement
cat >> .env << EOF
SENTRY_DSN=https://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=vectort-generated-code
EOF

# 4. Restart backend
sudo supervisorctl restart backend

# 5. Vérifier logs
tail -f /var/log/supervisor/backend.out.log

# 6. Test endpoints
curl http://localhost:8001/api/metrics
```

---

## 📖 Documentation Utilisateur

### Nouveaux Limits API:

```
Générations par minute:
- Free:       10/min
- Starter:    30/min
- Pro:        100/min
- Enterprise: Unlimited

Note: Les requêtes en cache ne comptent pas vers la limite.
```

---

**Prochaine étape:** Phase 1 complète (Celery + Redis queue)
**Estimé:** +4-6 semaines après quick wins
**Document:** Voir `/app/ROADMAP_EVOLUTION.md` Phase 1
