import React from "react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { ExternalLink, Rocket } from "lucide-react";

export default function DeploymentModal({ isOpen, onClose, githubUrl }) {
  const deploymentOptions = [
    {
      name: "Vercel",
      description: "Déploiement instantané pour React, Next.js, Vue",
      icon: "https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png",
      color: "black",
      url: githubUrl ? `https://vercel.com/new/clone?repository-url=${githubUrl}` : null
    },
    {
      name: "Netlify",
      description: "Hébergement rapide avec CI/CD automatique",
      icon: "https://www.netlify.com/v3/img/components/logomark.png",
      color: "#00C7B7",
      url: githubUrl ? `https://app.netlify.com/start/deploy?repository=${githubUrl}` : null
    },
    {
      name: "Railway",
      description: "Déploiement fullstack avec databases",
      icon: "https://railway.app/brand/logo-light.png",
      color: "#8B5CF6",
      url: githubUrl ? `https://railway.app/new/template?template=${githubUrl}` : null
    },
    {
      name: "Render",
      description: "Cloud platform pour applications modernes",
      icon: "https://render.com/favicon.ico",
      color: "#46E3B7",
      url: githubUrl ? `https://render.com/deploy?repo=${githubUrl}` : null
    }
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] bg-gray-900 text-white border-gray-700">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Rocket className="h-5 w-5 text-green-400" />
            Déployer votre application
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            {githubUrl 
              ? "Choisissez une plateforme pour déployer votre application en un clic"
              : "Exportez d'abord votre projet vers GitHub pour activer le déploiement"
            }
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-4">
          {!githubUrl ? (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">
                ⚠️ Vous devez d'abord exporter votre projet vers GitHub
              </p>
              <Button
                onClick={onClose}
                className="bg-green-600 hover:bg-green-700"
              >
                Compris
              </Button>
            </div>
          ) : (
            deploymentOptions.map((option) => (
              <div
                key={option.name}
                className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div 
                    className="w-10 h-10 rounded flex items-center justify-center"
                    style={{ backgroundColor: option.color }}
                  >
                    <img 
                      src={option.icon} 
                      alt={option.name}
                      className="w-6 h-6"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{option.name}</h3>
                    <p className="text-sm text-gray-400">{option.description}</p>
                  </div>
                </div>
                <Button
                  onClick={() => window.open(option.url, '_blank')}
                  className="bg-green-600 hover:bg-green-700"
                  size="sm"
                >
                  Déployer
                  <ExternalLink className="ml-2 h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </div>

        {githubUrl && (
          <div className="bg-gray-800 border border-gray-700 rounded p-3 text-sm">
            <p className="text-gray-400">
              💡 <strong className="text-white">Astuce :</strong> Ces plateformes détecteront automatiquement
              votre framework et configureront le build. Le déploiement prend généralement 2-5 minutes.
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
