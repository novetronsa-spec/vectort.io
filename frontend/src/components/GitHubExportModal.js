import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog";
import { Github, Lock, Globe, Loader2 } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function GitHubExportModal({ isOpen, onClose, projectId, projectTitle }) {
  const [githubToken, setGithubToken] = useState("");
  const [repoName, setRepoName] = useState(projectTitle || "");
  const [isPrivate, setIsPrivate] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  const handleExport = async () => {
    if (!githubToken.trim()) {
      toast({
        title: "Token requis",
        description: "Veuillez entrer votre token GitHub",
        variant: "destructive"
      });
      return;
    }

    setIsExporting(true);

    try {
      const response = await axios.post(`${API}/projects/${projectId}/export/github`, {
        github_token: githubToken,
        repo_name: repoName,
        private: isPrivate
      });

      if (response.data.success) {
        toast({
          title: "🎉 Export réussi !",
          description: `Projet exporté vers GitHub : ${response.data.repo_url}`,
        });

        // Ouvrir le repo dans un nouvel onglet
        window.open(response.data.repo_url, '_blank');
        
        onClose();
      }
    } catch (error) {
      console.error("Erreur export GitHub:", error);
      toast({
        title: "Erreur",
        description: error.response?.data?.detail || "Impossible d'exporter vers GitHub",
        variant: "destructive"
      });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px] bg-gray-900 text-white border-gray-700">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Github className="h-5 w-5" />
            Exporter vers GitHub
          </DialogTitle>
          <DialogDescription className="text-gray-400">
            Créez un nouveau repository GitHub et poussez votre code
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* GitHub Token */}
          <div className="space-y-2">
            <Label htmlFor="github-token" className="text-white">
              Token GitHub *
            </Label>
            <Input
              id="github-token"
              type="password"
              placeholder="ghp_xxxxxxxxxxxx"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="bg-gray-800 border-gray-700 text-white"
            />
            <p className="text-xs text-gray-400">
              Créez un token sur{" "}
              <a
                href="https://github.com/settings/tokens/new?scopes=repo"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-400 hover:underline"
              >
                GitHub Settings
              </a>
              {" "}avec la permission <code className="bg-gray-800 px-1 rounded">repo</code>
            </p>
          </div>

          {/* Repository Name */}
          <div className="space-y-2">
            <Label htmlFor="repo-name" className="text-white">
              Nom du repository
            </Label>
            <Input
              id="repo-name"
              type="text"
              placeholder="mon-projet-vectort"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              className="bg-gray-800 border-gray-700 text-white"
            />
          </div>

          {/* Private/Public */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="private-repo"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              className="w-4 h-4 rounded border-gray-700 bg-gray-800"
            />
            <Label htmlFor="private-repo" className="text-white cursor-pointer flex items-center gap-2">
              {isPrivate ? <Lock className="h-4 w-4" /> : <Globe className="h-4 w-4" />}
              Repository privé
            </Label>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onClose}
            className="bg-gray-800 text-white border-gray-700 hover:bg-gray-700"
          >
            Annuler
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting || !githubToken.trim()}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            {isExporting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Export en cours...
              </>
            ) : (
              <>
                <Github className="mr-2 h-4 w-4" />
                Exporter
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
