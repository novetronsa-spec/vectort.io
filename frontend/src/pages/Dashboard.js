import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Input } from "../components/ui/input";
import { 
  Plus, 
  Settings, 
  LogOut, 
  Play, 
  Code, 
  Globe, 
  Smartphone,
  Database,
  ArrowRight,
  Trash2,
  Edit3,
  Eye,
  Download,
  ExternalLink
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../hooks/use-toast";
import VoiceTextarea from "../components/VoiceTextarea";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { toast } = useToast();
  
  const [projects, setProjects] = useState([]);
  const [newProjectDescription, setNewProjectDescription] = useState(
    location.state?.description || ""
  );
  const [isCreating, setIsCreating] = useState(false);
  const [currentTab, setCurrentTab] = useState("projects");
  const [advancedMode, setAdvancedMode] = useState(false);
  const [selectedProjectType, setSelectedProjectType] = useState("web_app");
  const [selectedFramework, setSelectedFramework] = useState("react");
  const [selectedDatabase, setSelectedDatabase] = useState("mongodb");
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [stats, setStats] = useState({
    totalProjects: 0,
    activeProjects: 0,
    totalViews: 0
  });
  const [credits, setCredits] = useState({
    free_credits: 10,
    monthly_credits: 0,
    purchased_credits: 0,
    total_available: 10,
    subscription_plan: "free"
  });
  const [showCreditModal, setShowCreditModal] = useState(false);

  const frameworks = {
    web_app: ["react", "vue", "angular", "nextjs", "svelte"],
    ecommerce: ["react", "nextjs", "vue", "nuxt"],
    social_media: ["react", "nextjs", "vue"],
    saas_platform: ["react", "nextjs", "angular"],
    mobile_app: ["react_native", "flutter", "ionic"],
    rest_api: ["fastapi", "django", "flask", "express", "nestjs"],
    smart_contract: ["solidity"],
    ml_model: ["fastapi", "django", "flask"]
  };

  const databases = ["mongodb", "postgresql", "mysql", "firebase", "supabase"];
  
  const availableFeatures = [
    "Authentication", "Payment Processing", "Real-time Chat", "File Upload",
    "Email Notifications", "Push Notifications", "Analytics", "SEO Optimization",
    "Admin Dashboard", "Multi-language", "Dark/Light Theme", "API Documentation"
  ];

  useEffect(() => {
    fetchProjects();
    fetchUserStats();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Erreur lors du chargement des projets:", error);
    }
  };

  const fetchUserStats = async () => {
    try {
      const response = await axios.get(`${API}/users/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Erreur lors du chargement des statistiques:", error);
    }
  };

  const createProject = async () => {
    if (!newProjectDescription.trim()) {
      toast({
        title: "Description requise",
        description: "Veuillez décrire votre projet avant de le créer.",
        variant: "destructive"
      });
      return;
    }

    setIsCreating(true);
    try {
      // Create the project first
      const projectResponse = await axios.post(`${API}/projects`, {
        title: `${projectTypes.find(t => t.id === selectedProjectType)?.name} - ${projects.length + 1}`,
        description: newProjectDescription,
        type: selectedProjectType
      });

      const newProject = projectResponse.data;
      setProjects([newProject, ...projects]);
      
      toast({
        title: "Projet créé !",
        description: `Génération ${advancedMode ? 'avancée' : 'rapide'} en cours...`,
      });

      // Generate the application code using ADVANCED AI
      try {
        await axios.post(`${API}/projects/${newProject.id}/generate`, {
          description: newProjectDescription,
          type: selectedProjectType,
          framework: selectedFramework,
          database: selectedDatabase,
          features: selectedFeatures,
          integrations: [],
          deployment_target: "vercel",
          advanced_mode: advancedMode
        });

        // Refresh projects list to get updated status
        fetchProjects();
        
        toast({
          title: "Application générée !",
          description: "Votre application a été générée avec succès et est prête à être déployée.",
        });
      } catch (genError) {
        toast({
          title: "Génération échouée",
          description: "Le projet a été créé mais la génération du code a échoué.",
          variant: "destructive"
        });
      }

      setNewProjectDescription("");
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de créer le projet. Réessayez plus tard.",
        variant: "destructive"
      });
    }
    setIsCreating(false);
  };

  const deleteProject = async (projectId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}`);
      setProjects(projects.filter(p => p.id !== projectId));
      
      toast({
        title: "Projet supprimé",
        description: "Le projet a été supprimé avec succès.",
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de supprimer le projet.",
        variant: "destructive"
      });
    }
  };

  const openPreview = (projectId) => {
    const previewUrl = `${BACKEND_URL}/api/projects/${projectId}/preview`;
    window.open(previewUrl, '_blank');
  };

  const viewCode = async (projectId) => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}/code`);
      const codeData = response.data;
      
      // Create a simple code viewer modal (you could implement a proper modal)
      const codeContent = `
HTML:
${codeData.html_code || 'Aucun code HTML généré'}

CSS:
${codeData.css_code || 'Aucun code CSS généré'}

JavaScript:
${codeData.js_code || 'Aucun code JavaScript généré'}

React:
${codeData.react_code || 'Aucun code React généré'}

Backend:
${codeData.backend_code || 'Aucun code backend généré'}
      `;
      
      // For now, just copy to clipboard
      navigator.clipboard.writeText(codeContent);
      toast({
        title: "Code copié !",
        description: "Le code a été copié dans le presse-papiers.",
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de récupérer le code.",
        variant: "destructive"
      });
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const projectTypes = [
    // Applications Web
    { id: "web_app", name: "Application Web", icon: Globe, color: "bg-blue-600" },
    { id: "ecommerce", name: "E-commerce", icon: "🛒", color: "bg-green-600" },
    { id: "social_media", name: "Réseau Social", icon: "👥", color: "bg-purple-600" },
    { id: "saas_platform", name: "Plateforme SaaS", icon: "💼", color: "bg-indigo-600" },
    { id: "blog_cms", name: "Blog/CMS", icon: "📝", color: "bg-yellow-600" },
    { id: "portfolio", name: "Portfolio", icon: "🎨", color: "bg-pink-600" },
    { id: "dashboard", name: "Dashboard", icon: "📊", color: "bg-cyan-600" },
    
    // Mobile & PWA
    { id: "mobile_app", name: "App Mobile", icon: Smartphone, color: "bg-green-600" },
    { id: "pwa", name: "PWA", icon: "📱", color: "bg-teal-600" },
    { id: "react_native", name: "React Native", icon: "⚛️", color: "bg-blue-500" },
    
    // Backend & API
    { id: "rest_api", name: "API REST", icon: Database, color: "bg-purple-600" },
    { id: "graphql_api", name: "GraphQL API", icon: "🔗", color: "bg-pink-500" },
    { id: "microservices", name: "Microservices", icon: "🔧", color: "bg-gray-600" },
    
    // Blockchain & Web3
    { id: "smart_contract", name: "Smart Contract", icon: "⛓️", color: "bg-yellow-500" },
    { id: "dapp", name: "DApp", icon: "🌐", color: "bg-orange-500" },
    { id: "nft_marketplace", name: "NFT Marketplace", icon: "🖼️", color: "bg-purple-500" },
    
    // Gaming
    { id: "browser_game", name: "Jeu Browser", icon: "🎮", color: "bg-red-500" },
    { id: "mobile_game", name: "Jeu Mobile", icon: "🕹️", color: "bg-red-600" },
    
    // AI & Data
    { id: "ml_model", name: "Modèle ML", icon: "🤖", color: "bg-green-500" },
    { id: "chatbot", name: "Chatbot IA", icon: "💬", color: "bg-blue-400" },
    { id: "data_pipeline", name: "Pipeline Data", icon: "📈", color: "bg-indigo-500" },
    
    // Tools & Extensions
    { id: "cli_tool", name: "Outil CLI", icon: "⌨️", color: "bg-gray-500" },
    { id: "chrome_extension", name: "Extension Chrome", icon: "🧩", color: "bg-yellow-400" },
    
    // Classique
    { id: "landing_page", name: "Landing Page", icon: Code, color: "bg-orange-600" }
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold">vectort.io</h1>
            <Badge variant="outline" className="border-green-400 text-green-400">
              Dashboard
            </Badge>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-gray-400">Bienvenue, {user?.full_name}</span>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleLogout}
              className="text-red-400 hover:text-red-300"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <Tabs value={currentTab} onValueChange={setCurrentTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-gray-800 mb-8">
            <TabsTrigger value="projects" className="text-white data-[state=active]:bg-green-600">
              Mes Projets
            </TabsTrigger>
            <TabsTrigger value="create" className="text-white data-[state=active]:bg-green-600">
              Nouveau Projet
            </TabsTrigger>
            <TabsTrigger value="analytics" className="text-white data-[state=active]:bg-green-600">
              Analytiques
            </TabsTrigger>
          </TabsList>

          {/* Projects Tab */}
          <TabsContent value="projects" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold">Mes Projets</h2>
              <Button onClick={() => setCurrentTab("create")}>
                <Plus className="mr-2 h-4 w-4" />
                Nouveau Projet
              </Button>
            </div>

            {projects.length === 0 ? (
              <Card className="bg-gray-900 border-gray-700 text-center py-12">
                <CardContent>
                  <div className="text-gray-400 mb-4">
                    <Code className="mx-auto h-12 w-12 mb-4" />
                    <p className="text-xl mb-2">Aucun projet pour le moment</p>
                    <p>Créez votre premier projet pour commencer à construire quelque chose d'incroyable !</p>
                  </div>
                  <Button 
                    onClick={() => setCurrentTab("create")}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Créer un projet
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => {
                  const ProjectIcon = projectTypes.find(t => t.id === project.type)?.icon || Code;
                  const iconColor = projectTypes.find(t => t.id === project.type)?.color || "bg-gray-600";
                  
                  return (
                    <Card key={project.id} className="bg-gray-900 border-gray-700 hover:border-green-400 transition-colors">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className={`p-2 rounded-lg ${iconColor}`}>
                            <ProjectIcon className="h-5 w-5 text-white" />
                          </div>
                          <div className="flex space-x-1">
                            {project.status === 'completed' && (
                              <>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => openPreview(project.id)}
                                  title="Prévisualiser"
                                  className="text-blue-400 hover:text-blue-300"
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => viewCode(project.id)}
                                  title="Voir le code"
                                  className="text-green-400 hover:text-green-300"
                                >
                                  <Code className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => deleteProject(project.id)}
                              title="Supprimer"
                              className="text-red-400 hover:text-red-300"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        <CardTitle className="text-white">{project.title}</CardTitle>
                        <CardDescription className="text-gray-400">
                          {project.description.length > 100 
                            ? `${project.description.substring(0, 100)}...`
                            : project.description
                          }
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between mb-4">
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${
                              project.status === 'completed' ? 'border-green-400 text-green-400' :
                              project.status === 'building' ? 'border-yellow-400 text-yellow-400' :
                              project.status === 'error' ? 'border-red-400 text-red-400' :
                              'border-gray-400 text-gray-400'
                            }`}
                          >
                            {project.status === 'completed' ? '✅ Terminé' :
                             project.status === 'building' ? '⚡ Génération...' :
                             project.status === 'error' ? '❌ Erreur' :
                             '📝 Brouillon'}
                          </Badge>
                          {project.status === 'completed' ? (
                            <Button 
                              size="sm" 
                              onClick={() => openPreview(project.id)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <ExternalLink className="mr-2 h-4 w-4" />
                              Voir l'app
                            </Button>
                          ) : (
                            <Button size="sm" variant="outline" disabled>
                              <Play className="mr-2 h-4 w-4" />
                              En attente...
                            </Button>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          Créé le {new Date(project.created_at).toLocaleDateString('fr-FR')}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>

          {/* Create Project Tab */}
          <TabsContent value="create" className="space-y-6">
            <h2 className="text-3xl font-bold">Créer un nouveau projet</h2>
            
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Décrivez votre idée</CardTitle>
                <CardDescription>
                  Expliquez en détail ce que vous souhaitez construire. Plus vous êtes précis, 
                  meilleur sera le résultat.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <VoiceTextarea
                  placeholder="Ex: Je veux créer une application de gestion de tâches avec authentification, notifications en temps réel, et un design moderne... 🎤 Utilisez le micro pour décrire votre projet vocalement !"
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  className="min-h-32 bg-gray-800 border-gray-600 text-white resize-none"
                />
                
                {/* Toggle Mode Avancé */}
                <div className="mb-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium">Mode de génération</h3>
                    <div className="flex items-center space-x-3">
                      <span className={`text-sm ${!advancedMode ? 'text-green-400' : 'text-gray-400'}`}>
                        Rapide
                      </span>
                      <button
                        type="button"
                        onClick={() => setAdvancedMode(!advancedMode)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          advancedMode ? 'bg-green-600' : 'bg-gray-600'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            advancedMode ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                      <span className={`text-sm ${advancedMode ? 'text-green-400' : 'text-gray-400'}`}>
                        Avancé
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 mt-2">
                    {advancedMode 
                      ? "🚀 Génération complète avec architecture, fichiers de config, déploiement..." 
                      : "⚡ Génération rapide des fichiers principaux"
                    }
                  </p>
                </div>

                {/* Type de projet */}
                <div className="mb-6">
                  <h3 className="text-lg font-medium mb-4">Type de projet</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-80 overflow-y-auto">
                    {projectTypes.map((type) => {
                      const Icon = type.icon;
                      const isSelected = selectedProjectType === type.id;
                      return (
                        <Card 
                          key={type.id} 
                          onClick={() => setSelectedProjectType(type.id)}
                          className={`cursor-pointer transition-all p-3 ${
                            isSelected 
                              ? 'bg-green-600 border-green-400' 
                              : 'bg-gray-800 border-gray-600 hover:border-green-400'
                          }`}
                        >
                          <div className="text-center">
                            <div className={`p-2 rounded-lg ${isSelected ? 'bg-green-700' : type.color} inline-block mb-2`}>
                              {typeof type.icon === 'string' ? (
                                <span className="text-lg">{type.icon}</span>
                              ) : (
                                <Icon className="h-5 w-5 text-white" />
                              )}
                            </div>
                            <div className="text-xs font-medium">{type.name}</div>
                          </div>
                        </Card>
                      );
                    })}
                  </div>
                </div>

                {/* Options avancées */}
                {advancedMode && (
                  <div className="space-y-6 p-4 bg-gray-800 rounded-lg border border-green-400">
                    <h3 className="text-lg font-medium text-green-400">⚡ Options Avancées</h3>
                    
                    {/* Framework */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Framework</label>
                      <select
                        value={selectedFramework}
                        onChange={(e) => setSelectedFramework(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                      >
                        {(frameworks[selectedProjectType] || frameworks.web_app).map(fw => (
                          <option key={fw} value={fw}>{fw}</option>
                        ))}
                      </select>
                    </div>

                    {/* Base de données */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Base de données</label>
                      <select
                        value={selectedDatabase}
                        onChange={(e) => setSelectedDatabase(e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                      >
                        {databases.map(db => (
                          <option key={db} value={db}>{db}</option>
                        ))}
                      </select>
                    </div>

                    {/* Fonctionnalités */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">Fonctionnalités à inclure</label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
                        {availableFeatures.map(feature => (
                          <label key={feature} className="flex items-center space-x-2 text-sm">
                            <input
                              type="checkbox"
                              checked={selectedFeatures.includes(feature)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedFeatures([...selectedFeatures, feature]);
                                } else {
                                  setSelectedFeatures(selectedFeatures.filter(f => f !== feature));
                                }
                              }}
                              className="rounded bg-gray-700 border-gray-600 text-green-600"
                            />
                            <span className="text-gray-300">{feature}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                <Button 
                  onClick={createProject}
                  disabled={isCreating || !newProjectDescription.trim()}
                  className="w-full bg-green-600 hover:bg-green-700 py-6 text-lg"
                >
                  {isCreating ? "Création en cours..." : "Commencer à construire"}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <h2 className="text-3xl font-bold">Analytiques</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-2xl">{stats.totalProjects}</CardTitle>
                  <CardDescription>Projets Total</CardDescription>
                </CardHeader>
              </Card>
              
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-2xl">{stats.activeProjects}</CardTitle>
                  <CardDescription>Projets Actifs</CardDescription>
                </CardHeader>
              </Card>
              
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-2xl">{stats.totalViews}</CardTitle>
                  <CardDescription>Vues Total</CardDescription>
                </CardHeader>
              </Card>
            </div>

            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle>Activité récente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-gray-400">
                  Les analytiques détaillées seront bientôt disponibles...
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}