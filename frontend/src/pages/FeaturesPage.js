import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { 
  ArrowLeft, 
  Zap, 
  Palette, 
  Globe, 
  Code, 
  Smartphone, 
  Database,
  Shield,
  Rocket,
  Users,
  BarChart3,
  GitBranch,
  CheckCircle,
  ArrowRight
} from "lucide-react";

export default function FeaturesPage() {
  const navigate = useNavigate();

  const mainFeatures = [
    {
      icon: Zap,
      title: "IA Générative Avancée",
      description: "Transformez vos idées en applications complètes grâce à notre IA alimentée par GPT-4 et Claude Sonnet.",
      color: "text-yellow-400",
      bgColor: "from-yellow-400/10 to-yellow-600/10"
    },
    {
      icon: Palette,
      title: "Design Adaptatif",
      description: "Des interfaces modernes et responsives qui s'adaptent automatiquement à tous les appareils.",
      color: "text-purple-400",
      bgColor: "from-purple-400/10 to-purple-600/10"
    },
    {
      icon: Code,
      title: "Code de Production",
      description: "Génération de code propre, optimisé et prêt pour la production avec les meilleures pratiques.",
      color: "text-green-400",
      bgColor: "from-green-400/10 to-green-600/10"
    },
    {
      icon: Rocket,
      title: "Déploiement Instantané",
      description: "Déployez vos applications en un clic sur notre infrastructure cloud ou vos propres serveurs.",
      color: "text-blue-400",
      bgColor: "from-blue-400/10 to-blue-600/10"
    }
  ];

  const detailFeatures = [
    {
      category: "Développement",
      icon: Code,
      items: [
        "Frontend React/Vue/Angular",
        "Backend Node.js/Python/Go",
        "Base de données PostgreSQL/MongoDB",
        "API REST et GraphQL",
        "Authentification OAuth",
        "Intégrations tiers"
      ]
    },
    {
      category: "Design & UX",
      icon: Palette,
      items: [
        "Templates professionnels",
        "Composants personnalisables",
        "Animations fluides",
        "Design system cohérent",
        "Accessibilité WCAG",
        "Dark/Light mode"
      ]
    },
    {
      category: "Plateforme",
      icon: Globe,
      items: [
        "Multi-plateforme (Web/Mobile)",
        "PWA natif",
        "SEO optimisé",
        "Performance A+",
        "CDN global",
        "SSL automatique"
      ]
    },
    {
      category: "Collaboration",
      icon: Users,
      items: [
        "Équipes illimitées",
        "Commentaires temps réel",
        "Versionning Git",
        "Review de code",
        "Permissions granulaires",
        "Notifications intelligentes"
      ]
    },
    {
      category: "Analytics",
      icon: BarChart3,
      items: [
        "Métriques temps réel",
        "Comportement utilisateur",
        "Performance monitoring",
        "A/B testing",
        "Conversion tracking",
        "Rapports personnalisés"
      ]
    },
    {
      category: "Sécurité",
      icon: Shield,
      items: [
        "Chiffrement end-to-end",
        "Conformité RGPD",
        "Audit de sécurité",
        "Backup automatique",
        "2FA obligatoire",
        "Surveillance 24/7"
      ]
    }
  ];

  const integrations = [
    { name: "GitHub", logo: "🐱", description: "Synchronisation de code" },
    { name: "Stripe", logo: "💳", description: "Paiements en ligne" },
    { name: "Firebase", logo: "🔥", description: "Backend-as-a-Service" },
    { name: "Vercel", logo: "▲", description: "Déploiement automatique" },
    { name: "AWS", logo: "☁️", description: "Infrastructure cloud" },
    { name: "Slack", logo: "💬", description: "Notifications équipe" },
    { name: "Google Analytics", logo: "📊", description: "Analytics web" },
    { name: "Mailgun", logo: "📧", description: "Service email" }
  ];

  const useCases = [
    {
      title: "E-commerce",
      description: "Boutiques en ligne complètes avec gestion des stocks, paiements et expédition.",
      icon: "🛒",
      examples: ["Marketplace", "Boutique mode", "Digital products"]
    },
    {
      title: "SaaS Applications",
      description: "Plateformes software-as-a-service avec abonnements et analytics.",
      icon: "💻",
      examples: ["CRM", "Project management", "Analytics tools"]
    },
    {
      title: "Sites Vitrines",
      description: "Sites web professionnels pour présenter votre activité et convertir.",
      icon: "🌐",
      examples: ["Portfolio", "Corporate", "Landing pages"]
    },
    {
      title: "Applications Mobiles",
      description: "Apps natives iOS/Android ou Progressive Web Apps performantes.",
      icon: "📱",
      examples: ["Social app", "Fitness tracker", "Food delivery"]
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <nav className="flex justify-between items-center px-8 py-6 border-b border-gray-800">
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate("/")}
            className="text-gray-400 hover:text-white"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            vectort.io
          </Button>
        </div>
        <div className="flex items-center space-x-8">
          <span className="text-green-400 font-medium">Features</span>
          <a href="/pricing" className="hover:text-green-400 transition-colors">Pricing</a>
          <a href="#faqs" className="hover:text-green-400 transition-colors">FAQs</a>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-white text-black hover:bg-gray-200"
          >
            Commencer
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6">
            Des <span className="text-green-400">fonctionnalités</span> qui changent tout
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Découvrez comment Vectort révolutionne la création d'applications avec une suite complète 
            d'outils alimentés par l'intelligence artificielle.
          </p>
          <Badge variant="outline" className="border-green-400 text-green-400 text-lg px-4 py-2">
            ⚡ Powered by GPT-4 & Claude Sonnet
          </Badge>
        </div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          {mainFeatures.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="bg-gray-900 border-gray-700 hover:border-green-400 transition-all duration-300 group">
                <CardHeader className="text-center">
                  <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${feature.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className={`h-8 w-8 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl text-white">{feature.title}</CardTitle>
                  <CardDescription className="text-gray-400">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* Detailed Features */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center mb-12">
            Fonctionnalités <span className="text-green-400">complètes</span>
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {detailFeatures.map((category, index) => {
              const Icon = category.icon;
              return (
                <Card key={index} className="bg-gray-900 border-gray-700">
                  <CardHeader>
                    <div className="flex items-center space-x-3 mb-4">
                      <Icon className="h-6 w-6 text-green-400" />
                      <CardTitle className="text-lg text-white">{category.category}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {category.items.map((item, idx) => (
                        <div key={idx} className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-400 flex-shrink-0" />
                          <span className="text-gray-300 text-sm">{item}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Use Cases */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center mb-12">
            Cas d'<span className="text-green-400">usage</span>
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {useCases.map((useCase, index) => (
              <Card key={index} className="bg-gray-900 border-gray-700 hover:border-green-400 transition-colors">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl">{useCase.icon}</div>
                    <div>
                      <CardTitle className="text-xl text-white">{useCase.title}</CardTitle>
                      <CardDescription className="text-gray-400 mt-2">
                        {useCase.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {useCase.examples.map((example, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {example}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Integrations */}
        <div className="mb-20">
          <h2 className="text-3xl font-bold text-center mb-4">
            Intégrations <span className="text-green-400">natives</span>
          </h2>
          <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
            Connectez facilement vos outils préférés pour créer des workflows automatisés.
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {integrations.map((integration, index) => (
              <Card key={index} className="bg-gray-900 border-gray-700 hover:border-green-400 transition-colors text-center">
                <CardContent className="p-6">
                  <div className="text-3xl mb-3">{integration.logo}</div>
                  <h3 className="font-semibold text-white mb-2">{integration.name}</h3>
                  <p className="text-xs text-gray-400">{integration.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-12 border border-gray-700">
          <h2 className="text-3xl font-bold mb-4">
            Prêt à découvrir la <span className="text-green-400">puissance</span> de Codex ?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Rejoignez des milliers de développeurs et créateurs qui utilisent déjà Codex 
            pour transformer leurs idées en applications performantes.
          </p>
          <div className="flex justify-center space-x-4">
            <Button 
              onClick={() => navigate("/auth")}
              className="bg-green-600 hover:bg-green-700 px-8 py-4 text-lg font-medium"
            >
              Commencer gratuitement
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button 
              onClick={() => navigate("/pricing")}
              variant="outline" 
              className="border-gray-600 text-gray-300 px-8 py-4 text-lg"
            >
              Voir les prix
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}