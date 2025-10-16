import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Check, ArrowLeft, Zap, Star, Sparkles, CreditCard } from "lucide-react";

export default function PricingPage() {
  const navigate = useNavigate();

  const creditPackages = [
    {
      name: "Starter",
      credits: 100,
      price: 20,
      description: "Parfait pour commencer",
      icon: Zap,
      color: "text-green-400",
      bgColor: "from-green-400/10 to-green-600/10",
      borderColor: "border-green-400/50",
      features: [
        "100 crédits",
        "~50 générations rapides",
        "~25 générations avancées",
        "Pas d'expiration",
        "Tous les types de projets",
        "24+ frameworks supportés"
      ],
      savings: null,
      buttonText: "Acheter 100 crédits",
      buttonVariant: "outline"
    },
    {
      name: "Standard",
      credits: 250,
      price: 50,
      description: "Meilleure valeur",
      icon: Star,
      color: "text-purple-400",
      bgColor: "from-purple-400/10 to-purple-600/10",
      borderColor: "border-purple-400/50",
      popular: true,
      features: [
        "250 crédits",
        "~125 générations rapides",
        "~62 générations avancées",
        "Pas d'expiration",
        "Tous les types de projets",
        "Mode avancé illimité",
        "Support prioritaire"
      ],
      savings: "Économisez $12.50",
      buttonText: "Acheter 250 crédits",
      buttonVariant: "default"
    },
    {
      name: "Pro",
      credits: 400,
      price: 80,
      description: "Maximum d'économies",
      icon: Sparkles,
      color: "text-orange-400",
      bgColor: "from-orange-400/10 to-orange-600/10",
      borderColor: "border-orange-400/50",
      features: [
        "400 crédits",
        "~200 générations rapides",
        "~100 générations avancées",
        "Pas d'expiration",
        "Tous les types de projets",
        "Génération prioritaire",
        "Support dédié",
        "Accès anticipé aux features"
      ],
      savings: "Économisez $20.00",
      buttonText: "Acheter 400 crédits",
      buttonVariant: "outline"
    }
  ];

  const faqs = [
    {
      question: "Comment fonctionnent les crédits ?",
      answer: "Chaque génération d'application consomme des crédits. Les générations rapides coûtent 2 crédits, les générations avancées coûtent 4 crédits. Vous recevez 10 crédits gratuits à l'inscription."
    },
    {
      question: "Les crédits expirent-ils ?",
      answer: "Non ! Tous les crédits achetés n'expirent jamais. Vous pouvez les utiliser quand vous voulez, à votre rythme."
    },
    {
      question: "Puis-je acheter des crédits plusieurs fois ?",
      answer: "Oui, vous pouvez acheter autant de packages que vous le souhaitez. Tous les crédits s'accumulent dans votre compte."
    },
    {
      question: "Que se passe-t-il si je manque de crédits pendant une génération ?",
      answer: "L'application vérifie votre solde avant chaque génération. Si vous n'avez pas assez de crédits, vous serez invité à recharger votre compte."
    },
    {
      question: "Y a-t-il une garantie de remboursement ?",
      answer: "Oui, nous offrons une garantie de remboursement de 30 jours sur tous les achats de crédits."
    },
    {
      question: "Le paiement est-il sécurisé ?",
      answer: "Oui, tous les paiements sont traités de manière sécurisée via Stripe, un leader mondial du paiement en ligne. Nous ne stockons jamais vos informations de carte bancaire."
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
            Rechargez vos <span className="text-green-400">crédits</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Achetez des crédits pour générer vos applications avec l'IA. 
            Aucun abonnement, pas d'expiration.
          </p>
          
          <div className="flex items-center justify-center mt-8 space-x-4">
            <Badge variant="outline" className="border-green-400 text-green-400">
              ✨ 10 crédits gratuits à l'inscription
            </Badge>
            <Badge variant="outline" className="border-blue-400 text-blue-400">
              🔒 Paiement sécurisé par Stripe
            </Badge>
            <Badge variant="outline" className="border-purple-400 text-purple-400">
              ⚡ Pas d'expiration
            </Badge>
          </div>
        </div>

        {/* Credit Usage Info */}
        <div className="max-w-3xl mx-auto mb-12">
          <Card className="bg-gradient-to-br from-green-900/30 to-gray-900 border-green-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-center space-x-8 text-center">
                <div>
                  <div className="text-3xl font-bold text-green-400">2</div>
                  <div className="text-sm text-gray-400">crédits</div>
                  <div className="text-xs text-gray-500 mt-1">Génération rapide</div>
                </div>
                <div className="h-12 w-px bg-gray-700"></div>
                <div>
                  <div className="text-3xl font-bold text-purple-400">4</div>
                  <div className="text-sm text-gray-400">crédits</div>
                  <div className="text-xs text-gray-500 mt-1">Génération avancée</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {creditPackages.map((pkg, index) => {
            const Icon = pkg.icon;
            return (
              <Card 
                key={pkg.name}
                className={`relative bg-gray-900 ${pkg.borderColor} ${
                  pkg.popular ? 'ring-2 ring-purple-400 scale-105' : 'border-gray-700'
                } hover:border-green-400 transition-all duration-300`}
              >
                {pkg.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-purple-600 text-white px-4 py-1">
                      POPULAIRE
                    </Badge>
                  </div>
                )}
                
                <CardHeader className="text-center pb-8">
                  <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${pkg.bgColor} flex items-center justify-center mb-4`}>
                    <Icon className={`h-8 w-8 ${pkg.color}`} />
                  </div>
                  
                  <CardTitle className="text-2xl text-white">{pkg.name}</CardTitle>
                  <CardDescription className="text-gray-400">{pkg.description}</CardDescription>
                  
                  <div className="mt-6">
                    <div className="text-5xl font-bold text-white mb-2">{pkg.credits}</div>
                    <div className="text-gray-400 mb-3">crédits</div>
                    <div className="flex items-baseline justify-center">
                      <span className="text-3xl font-bold text-green-400">${pkg.price}</span>
                      <span className="text-gray-400 ml-1">.00</span>
                    </div>
                    {pkg.savings && (
                      <div className="text-xs text-green-400 mt-2">{pkg.savings}</div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="space-y-3">
                    {pkg.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center space-x-3">
                        <Check className="h-5 w-5 text-green-400 flex-shrink-0" />
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    onClick={() => navigate("/auth")}
                    variant={pkg.buttonVariant}
                    className={`w-full py-6 text-lg font-medium ${
                      pkg.popular 
                        ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                        : 'border-green-400 text-green-400 hover:bg-green-400 hover:text-black'
                    }`}
                  >
                    {pkg.buttonText}
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