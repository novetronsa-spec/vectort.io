import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Check, ArrowLeft, Zap, Crown, Rocket } from "lucide-react";

export default function PricingPage() {
  const navigate = useNavigate();

  const plans = [
    {
      name: "Starter",
      price: "Gratuit",
      description: "Parfait pour débuter avec Vectort",
      icon: Zap,
      color: "text-green-400",
      bgColor: "from-green-400/10 to-green-600/10",
      borderColor: "border-green-400/50",
      features: [
        "3 projets par mois",
        "Templates de base",
        "Support communauté",
        "Déploiement sur sous-domaine",
        "Stockage 1GB"
      ],
      limitations: [
        "Pas de domaine personnalisé",
        "Watermark Vectort",
        "Support standard"
      ],
      buttonText: "Commencer gratuitement",
      buttonVariant: "outline"
    },
    {
      name: "Pro",
      price: "29€",
      period: "/mois",
      description: "Pour les créateurs sérieux",
      icon: Crown,
      color: "text-purple-400",
      bgColor: "from-purple-400/10 to-purple-600/10",
      borderColor: "border-purple-400/50",
      popular: true,
      features: [
        "Projets illimités",
        "Tous les templates premium",
        "IA avancée (GPT-4, Claude)",
        "Domaine personnalisé",
        "Stockage 50GB",
        "Support prioritaire",
        "Analytics avancés",
        "Collaborateurs (5 max)",
        "Déploiement automatique",
        "SSL gratuit"
      ],
      buttonText: "Démarrer l'essai Pro",
      buttonVariant: "default"
    },
    {
      name: "Enterprise",
      price: "199€",
      period: "/mois",
      description: "Pour les équipes et entreprises",
      icon: Rocket,
      color: "text-orange-400",
      bgColor: "from-orange-400/10 to-orange-600/10",
      borderColor: "border-orange-400/50",
      features: [
        "Tout de Pro +",
        "Équipe illimitée",
        "IA personnalisée",
        "Intégrations avancées",
        "Stockage 500GB",
        "Support dédié 24/7",
        "SLA 99.9%",
        "Sauvegardes automatiques",
        "Environnements multiples",
        "API dédiée",
        "Formation équipe",
        "Déploiement on-premise"
      ],
      buttonText: "Contacter l'équipe",
      buttonVariant: "outline"
    }
  ];

  const faqs = [
    {
      question: "Puis-je changer de plan à tout moment ?",
      answer: "Oui, vous pouvez upgrader ou downgrader votre plan à tout moment. Les changements sont effectifs immédiatement."
    },
    {
      question: "Que se passe-t-il si je dépasse les limites de mon plan ?",
      answer: "Nous vous notifierons avant d'atteindre les limites. Vous pouvez soit upgrader votre plan soit attendre le prochain cycle."
    },
    {
      question: "Y a-t-il une garantie de remboursement ?",
      answer: "Oui, nous offrons une garantie de remboursement de 30 jours sur tous nos plans payants."
    },
    {
      question: "Les prix incluent-ils la TVA ?",
      answer: "Les prix affichés sont hors taxes. La TVA applicable sera ajoutée lors du checkout selon votre localisation."
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
          <a href="#features" className="hover:text-green-400 transition-colors">Features</a>
          <span className="text-green-400 font-medium">Pricing</span>
          <a href="#faqs" className="hover:text-green-400 transition-colors">FAQs</a>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-white text-black hover:bg-gray-200"
          >
            Commencer
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">
            Choisissez votre <span className="text-green-400">plan</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Des plans flexibles pour tous vos besoins de création. 
            Commencez gratuitement, évoluez quand vous voulez.
          </p>
          
          <div className="flex items-center justify-center mt-8 space-x-4">
            <Badge variant="outline" className="border-green-400 text-green-400">
              ✨ 30 jours d'essai gratuit
            </Badge>
            <Badge variant="outline" className="border-blue-400 text-blue-400">
              🔒 Sans engagement
            </Badge>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            return (
              <Card 
                key={plan.name}
                className={`relative bg-gray-900 ${plan.borderColor} ${
                  plan.popular ? 'ring-2 ring-purple-400 scale-105' : 'border-gray-700'
                } hover:border-green-400 transition-all duration-300`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-purple-600 text-white px-4 py-1">
                      Le plus populaire
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-8">
                  <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${plan.bgColor} flex items-center justify-center mb-4`}>
                    <Icon className={`h-8 w-8 ${plan.color}`} />
                  </div>
                  
                  <CardTitle className="text-2xl text-white">{plan.name}</CardTitle>
                  <CardDescription className="text-gray-400">{plan.description}</CardDescription>
                  
                  <div className="mt-6">
                    <div className="flex items-baseline justify-center">
                      <span className="text-4xl font-bold text-white">{plan.price}</span>
                      {plan.period && <span className="text-gray-400 ml-2">{plan.period}</span>}
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center space-x-3">
                        <Check className="h-5 w-5 text-green-400 flex-shrink-0" />
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {plan.limitations && (
                    <div className="pt-4 border-t border-gray-800">
                      <p className="text-xs text-gray-500 mb-2">Limitations :</p>
                      {plan.limitations.map((limitation, idx) => (
                        <p key={idx} className="text-xs text-gray-500">
                          • {limitation}
                        </p>
                      ))}
                    </div>
                  )}

                  <Button 
                    onClick={() => navigate("/auth")}
                    variant={plan.buttonVariant}
                    className={`w-full py-6 text-lg font-medium ${
                      plan.popular 
                        ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                        : plan.buttonVariant === 'outline' 
                          ? 'border-green-400 text-green-400 hover:bg-green-400 hover:text-black'
                          : 'bg-green-600 hover:bg-green-700'
                    }`}
                  >
                    {plan.buttonText}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Enterprise Contact */}
        <div className="text-center mb-16">
          <Card className="bg-gradient-to-r from-gray-900 to-gray-800 border-gray-700 max-w-4xl mx-auto">
            <CardContent className="p-12">
              <h3 className="text-3xl font-bold mb-4">Besoin d'une solution personnalisée ?</h3>
              <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
                Notre équipe est là pour créer une solution sur mesure qui correspond parfaitement 
                à vos besoins spécifiques et à votre budget.
              </p>
              <div className="flex justify-center space-x-4">
                <Button className="bg-green-600 hover:bg-green-700 px-8 py-3">
                  Planifier une démo
                </Button>
                <Button variant="outline" className="border-gray-600 text-gray-300 px-8 py-3">
                  Nous contacter
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* FAQ Section */}
        <div id="faqs" className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Questions <span className="text-green-400">fréquentes</span>
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {faqs.map((faq, index) => (
              <Card key={index} className="bg-gray-900 border-gray-700">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-white mb-3">{faq.question}</h3>
                  <p className="text-gray-400">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-16">
          <h2 className="text-3xl font-bold mb-4">
            Prêt à transformer vos idées en <span className="text-green-400">réalité</span> ?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Rejoignez des milliers de créateurs qui font confiance à Codex pour donner vie à leurs projets.
          </p>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-green-600 hover:bg-green-700 px-8 py-4 text-lg font-medium"
          >
            Commencer maintenant - C'est gratuit
          </Button>
        </div>
      </div>
    </div>
  );
}