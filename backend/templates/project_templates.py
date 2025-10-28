"""
Système de Templates Professionnels pour Vectort.io
Templates pré-configurés pour tous types de projets

Catégories:
- Web Apps (E-commerce, SaaS, Blog, Portfolio)
- APIs (REST, GraphQL, gRPC)
- Mobile (iOS, Android, Cross-platform)
- Desktop (Electron, Tauri)
- CLI Tools
- Microservices
- Data/ML
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ProjectTemplate:
    """Template de projet professionnel"""
    
    id: str
    name: str
    description: str
    category: str
    language: str
    framework: str
    complexity: str  # simple, medium, complex
    features: List[str]
    estimated_files: int
    estimated_time: int  # secondes
    fibonacci_priority: int  # 1-144
    icon: str
    tags: List[str]


class TemplateManager:
    """Gestionnaire de templates professionnels"""
    
    TEMPLATES = [
        # ===== WEB APPS =====
        ProjectTemplate(
            id="ecommerce-fullstack",
            name="E-Commerce Complet",
            description="Boutique en ligne avec panier, paiement Stripe, admin dashboard",
            category="web_app",
            language="javascript",
            framework="react",
            complexity="complex",
            features=[
                "🛒 Catalogue produits",
                "💳 Paiement Stripe",
                "👤 Auth JWT",
                "📊 Dashboard admin",
                "🔍 Recherche & filtres",
                "📱 Responsive design"
            ],
            estimated_files=45,
            estimated_time=90,
            fibonacci_priority=89,
            icon="🛍️",
            tags=["react", "stripe", "jwt", "admin"]
        ),
        
        ProjectTemplate(
            id="saas-platform",
            name="Plateforme SaaS",
            description="SaaS multi-tenant avec subscriptions, analytics, team management",
            category="web_app",
            language="typescript",
            framework="nextjs",
            complexity="complex",
            features=[
                "🏢 Multi-tenant",
                "💰 Subscriptions (Stripe)",
                "📈 Analytics dashboard",
                "👥 Team management",
                "🔐 Role-based access",
                "📧 Email notifications"
            ],
            estimated_files=55,
            estimated_time=100,
            fibonacci_priority=144,
            icon="🚀",
            tags=["nextjs", "saas", "subscriptions", "analytics"]
        ),
        
        ProjectTemplate(
            id="blog-cms",
            name="Blog & CMS",
            description="Blog professionnel avec CMS, SEO, comments, newsletter",
            category="web_app",
            language="python",
            framework="django",
            complexity="medium",
            features=[
                "📝 CMS admin",
                "💬 Comments système",
                "🔍 SEO optimisé",
                "📧 Newsletter",
                "🏷️ Tags & catégories",
                "👤 Multi-auteurs"
            ],
            estimated_files=35,
            estimated_time=70,
            fibonacci_priority=55,
            icon="📰",
            tags=["django", "cms", "blog", "seo"]
        ),
        
        # ===== APIs =====
        ProjectTemplate(
            id="rest-api-complete",
            name="API REST Complète",
            description="API REST avec auth, database, docs Swagger, rate limiting",
            category="api_rest",
            language="python",
            framework="fastapi",
            complexity="medium",
            features=[
                "🔐 Auth JWT",
                "🗄️ Database (PostgreSQL)",
                "📚 Swagger docs",
                "⚡ Rate limiting",
                "🧪 Tests unitaires",
                "🐳 Docker ready"
            ],
            estimated_files=30,
            estimated_time=60,
            fibonacci_priority=34,
            icon="🔌",
            tags=["fastapi", "rest", "jwt", "swagger"]
        ),
        
        ProjectTemplate(
            id="graphql-api",
            name="API GraphQL",
            description="API GraphQL avec Apollo, subscriptions, caching",
            category="api_graphql",
            language="javascript",
            framework="express",
            complexity="complex",
            features=[
                "📊 GraphQL schema",
                "🔄 Subscriptions temps réel",
                "💾 Redis caching",
                "🔐 Auth & permissions",
                "🧪 Testing",
                "📈 Monitoring"
            ],
            estimated_files=40,
            estimated_time=80,
            fibonacci_priority=55,
            icon="🎯",
            tags=["graphql", "apollo", "subscriptions", "redis"]
        ),
        
        # ===== MOBILE =====
        ProjectTemplate(
            id="mobile-cross-platform",
            name="App Mobile Cross-Platform",
            description="Application mobile iOS/Android avec React Native",
            category="mobile_app",
            language="javascript",
            framework="react_native",
            complexity="complex",
            features=[
                "📱 iOS + Android",
                "🔐 Auth biométrique",
                "📡 Offline mode",
                "🔔 Push notifications",
                "📸 Caméra intégrée",
                "🗺️ Maps & géolocalisation"
            ],
            estimated_files=50,
            estimated_time=95,
            fibonacci_priority=89,
            icon="📱",
            tags=["react-native", "ios", "android", "mobile"]
        ),
        
        ProjectTemplate(
            id="flutter-app",
            name="App Flutter",
            description="Application mobile Flutter avec Firebase",
            category="mobile_app",
            language="dart",
            framework="flutter",
            complexity="complex",
            features=[
                "🎨 Material Design",
                "🔥 Firebase integration",
                "💬 Chat temps réel",
                "📷 Upload photos",
                "🔔 Notifications",
                "🌐 Multi-langue"
            ],
            estimated_files=45,
            estimated_time=90,
            fibonacci_priority=89,
            icon="🦋",
            tags=["flutter", "firebase", "material", "dart"]
        ),
        
        # ===== MICROSERVICES =====
        ProjectTemplate(
            id="microservices-architecture",
            name="Architecture Microservices",
            description="3 microservices avec API Gateway, service discovery, monitoring",
            category="microservice",
            language="go",
            framework="gin",
            complexity="complex",
            features=[
                "🌐 API Gateway",
                "🔍 Service discovery",
                "📊 Monitoring (Prometheus)",
                "🔄 Load balancing",
                "🐳 Docker Compose",
                "☸️ Kubernetes ready"
            ],
            estimated_files=60,
            estimated_time=110,
            fibonacci_priority=144,
            icon="🏗️",
            tags=["microservices", "go", "kubernetes", "docker"]
        ),
        
        # ===== CLI TOOLS =====
        ProjectTemplate(
            id="cli-tool-advanced",
            name="CLI Tool Avancé",
            description="Outil CLI avec subcommands, config, auto-completion",
            category="cli_tool",
            language="python",
            framework="click",
            complexity="simple",
            features=[
                "⌨️ Subcommands",
                "⚙️ Config file",
                "🎨 Colored output",
                "📝 Auto-completion",
                "🧪 Tests",
                "📦 PyPI ready"
            ],
            estimated_files=20,
            estimated_time=40,
            fibonacci_priority=21,
            icon="⚡",
            tags=["cli", "python", "click", "tool"]
        ),
        
        # ===== DATA / ML =====
        ProjectTemplate(
            id="ml-api",
            name="ML API avec FastAPI",
            description="API ML avec modèle pré-entraîné, predictions, monitoring",
            category="machine_learning",
            language="python",
            framework="fastapi",
            complexity="complex",
            features=[
                "🤖 Modèle ML intégré",
                "🔮 Endpoint predictions",
                "📊 Model monitoring",
                "💾 Model versioning",
                "🧪 Testing ML",
                "📈 Performance metrics"
            ],
            estimated_files=35,
            estimated_time=75,
            fibonacci_priority=55,
            icon="🤖",
            tags=["ml", "fastapi", "ai", "predictions"]
        ),
        
        ProjectTemplate(
            id="data-pipeline",
            name="Pipeline de Données",
            description="ETL pipeline avec Airflow, dbt, data validation",
            category="data_pipeline",
            language="python",
            framework="airflow",
            complexity="complex",
            features=[
                "🔄 ETL orchestration",
                "📊 Data transformations",
                "✅ Data validation",
                "📈 Monitoring",
                "🗄️ Multi databases",
                "📧 Alerting"
            ],
            estimated_files=40,
            estimated_time=85,
            fibonacci_priority=89,
            icon="🔀",
            tags=["data", "etl", "airflow", "pipeline"]
        )
    ]
    
    @classmethod
    def get_all_templates(cls) -> List[ProjectTemplate]:
        """Retourne tous les templates"""
        return cls.TEMPLATES
    
    @classmethod
    def get_template(cls, template_id: str) -> ProjectTemplate:
        """Récupère un template par ID"""
        for template in cls.TEMPLATES:
            if template.id == template_id:
                return template
        return None
    
    @classmethod
    def get_templates_by_category(cls, category: str) -> List[ProjectTemplate]:
        """Récupère templates par catégorie"""
        return [t for t in cls.TEMPLATES if t.category == category]
    
    @classmethod
    def get_templates_by_complexity(cls, complexity: str) -> List[ProjectTemplate]:
        """Récupère templates par complexité"""
        return [t for t in cls.TEMPLATES if t.complexity == complexity]
    
    @classmethod
    def search_templates(cls, query: str) -> List[ProjectTemplate]:
        """Recherche templates par nom, description ou tags"""
        query = query.lower()
        results = []
        
        for template in cls.TEMPLATES:
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag for tag in template.tags)):
                results.append(template)
        
        return results
    
    @classmethod
    def get_template_stats(cls) -> Dict:
        """Statistiques sur les templates"""
        
        categories = {}
        languages = {}
        complexities = {"simple": 0, "medium": 0, "complex": 0}
        
        for template in cls.TEMPLATES:
            # Par catégorie
            categories[template.category] = categories.get(template.category, 0) + 1
            
            # Par langage
            languages[template.language] = languages.get(template.language, 0) + 1
            
            # Par complexité
            complexities[template.complexity] += 1
        
        return {
            "total_templates": len(cls.TEMPLATES),
            "categories": categories,
            "languages": languages,
            "complexities": complexities
        }


# Export
__all__ = ['ProjectTemplate', 'TemplateManager']
