import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../hooks/use-toast";

export default function AuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, register } = useAuth();
  const { toast } = useToast();
  
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState([]);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    fullName: ""
  });

  const description = location.state?.description || "";

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      toast({
        title: "Connexion réussie !",
        description: "Vous êtes maintenant connecté à Codex.",
      });
      navigate(description ? "/dashboard" : "/dashboard", { state: { description } });
    } else {
      toast({
        title: "Erreur de connexion",
        description: result.error,
        variant: "destructive"
      });
    }
    
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await register(formData.email, formData.password, formData.fullName);
    
    if (result.success) {
      toast({
        title: "Compte créé avec succès !",
        description: "Bienvenue sur Codex.",
      });
      navigate(description ? "/dashboard" : "/dashboard", { state: { description } });
    } else {
      toast({
        title: "Erreur d'inscription",
        description: result.error,
        variant: "destructive"
      });
    }
    
    setLoading(false);
  };

  const handleOAuthSignIn = (provider) => {
    toast({
      title: "Authentification OAuth",
      description: `Connexion ${provider} en cours de développement...`,
    });
  };

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        {/* Back button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate("/")}
          className="mb-8 text-gray-400 hover:text-white"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour à l'accueil
        </Button>

        {/* Brand */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">codex</h1>
          <p className="text-gray-400">
            Où les idées deviennent <span className="text-green-400">réalité</span>
          </p>
        </div>

        <Card className="bg-gray-900 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white text-center">Rejoignez Codex</CardTitle>
            <CardDescription className="text-gray-400 text-center">
              Créez des applications incroyables avec l'IA
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-gray-800">
                <TabsTrigger value="login" className="text-white data-[state=active]:bg-green-600">
                  Connexion
                </TabsTrigger>
                <TabsTrigger value="register" className="text-white data-[state=active]:bg-green-600">
                  S'inscrire
                </TabsTrigger>
              </TabsList>

              {/* OAuth Buttons */}
              <div className="space-y-3 mt-6">
                <Button 
                  onClick={() => handleOAuthSignIn("Google")}
                  className="w-full bg-white text-black hover:bg-gray-200"
                >
                  <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continuer avec Google
                </Button>

                <div className="flex space-x-3">
                  <Button 
                    onClick={() => handleOAuthSignIn("GitHub")}
                    variant="outline" 
                    className="flex-1 bg-transparent border-gray-600 text-white hover:bg-gray-800"
                  >
                    <svg className="mr-2 h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.477 2 2 6.59 2 12.253c0 4.53 2.865 8.373 6.839 9.728.5.093.683-.217.683-.489 0-.243-.009-1.051-.013-1.91-2.782.605-3.369-1.235-3.369-1.235-.454-1.184-1.11-1.499-1.11-1.499-.908-.634.069-.621.069-.621 1.004.072 1.533 1.056 1.533 1.056.892 1.568 2.341 1.115 2.91.853.09-.663.35-1.115.636-1.371-2.22-.253-4.555-1.132-4.555-5.04 0-1.113.39-2.028 1.03-2.744-.103-.253-.446-1.295.098-2.698 0 0 .84-.275 2.75 1.048A9.38 9.38 0 0112 6.958c.85.004 1.705.117 2.504.343 1.909-1.323 2.747-1.048 2.747-1.048.546 1.403.203 2.445.1 2.698.642.716 1.031 1.631 1.031 2.744 0 3.916-2.338 4.784-4.565 5.033.359.314.679.934.679 1.881 0 1.36-.012 2.457-.012 2.791 0 .274.18.586.688.486C19.137 20.622 22 16.78 22 12.253 22 6.59 17.523 2 12 2z"/>
                    </svg>
                    GitHub
                  </Button>
                  <Button 
                    onClick={() => handleOAuthSignIn("Apple")}
                    variant="outline" 
                    className="flex-1 bg-transparent border-gray-600 text-white hover:bg-gray-800"
                  >
                    <svg className="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.065 21.933c-1.176 1.14-2.459.96-3.695.49-1.308-.49-2.504-.514-3.867.49-1.726.842-2.635.622-3.655-.49C1.85 15.897 2.714 6.707 9.362 6.371c1.619.084 2.748.841 3.697.904 1.416-.269 2.771-.963 4.285-.822 1.818.142 3.183.83 4.049 2.441-3.744 2.241-2.856 7.147 1.256 9.002-.603 1.8-1.372 3.586-2.584 4.037zM12.042 6.299c-.118-2.677 2.153-4.878 4.636-4.799-.281 3.442-3.126 5.659-4.636 4.799z"/>
                    </svg>
                    Apple
                  </Button>
                </div>

                <div className="text-center text-gray-500 text-sm">Ou avec email</div>
              </div>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <Input
                      id="login-email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="bg-gray-800 border-gray-600 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password">Mot de passe</Label>
                    <div className="relative">
                      <Input
                        id="login-password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleInputChange}
                        className="bg-gray-800 border-gray-600 text-white pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                  >
                    {loading ? "Connexion..." : "Se connecter"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-name">Nom complet</Label>
                    <Input
                      id="register-name"
                      name="fullName"
                      type="text"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      className="bg-gray-800 border-gray-600 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <Input
                      id="register-email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="bg-gray-800 border-gray-600 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-password">Mot de passe</Label>
                    <div className="relative">
                      <Input
                        id="register-password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleInputChange}
                        className="bg-gray-800 border-gray-600 text-white pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  <Button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                  >
                    {loading ? "Inscription..." : "S'inscrire"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <p className="text-xs text-gray-500 text-center mt-4">
              En continuant, vous acceptez nos{" "}
              <a href="#" className="text-green-400 hover:underline">Conditions d'utilisation</a>{" "}
              et notre{" "}
              <a href="#" className="text-green-400 hover:underline">Politique de confidentialité</a>.
            </p>
          </CardContent>
        </Card>

        {description && (
          <Card className="mt-6 bg-green-900 border-green-600">
            <CardContent className="pt-6">
              <p className="text-sm text-green-100">
                <span className="font-medium">Votre idée :</span> "{description}"
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}