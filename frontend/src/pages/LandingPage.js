import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Badge } from "../components/ui/badge";
import { ArrowRight, ArrowLeft, ArrowDown, Star } from "lucide-react";
import VoiceTextarea from "../components/VoiceTextarea";
import { useAuth } from "../contexts/AuthContext";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [description, setDescription] = useState("");
  const [stats, setStats] = useState({
    users: "1.5M+",
    apps: "2M+", 
    countries: "180+"
  });

  const demoApps = [
    {
      title: "E-commerce Platform",
      image: "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=300&fit=crop",
      description: "Full-featured online store"
    },
    {
      title: "Social Media App",
      image: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop", 
      description: "Connect and share with friends"
    },
    {
      title: "Task Management",
      image: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop",
      description: "Organize your productivity"
    },
    {
      title: "Analytics Dashboard", 
      image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
      description: "Data visualization made easy"
    },
    {
      title: "Video Streaming",
      image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=400&h=300&fit=crop",
      description: "Content delivery platform"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % demoApps.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [demoApps.length]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/stats`);
        setStats(response.data);
      } catch (error) {
        console.log("Using default stats");
      }
    };
    fetchStats();
  }, []);

  const handleStartBuilding = () => {
    if (isAuthenticated) {
      navigate("/dashboard", { state: { description } });
    } else {
      navigate("/auth", { state: { description } });
    }
  };

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % demoApps.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + demoApps.length) % demoApps.length);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="flex justify-between items-center px-8 py-6">
        <div className="text-2xl font-bold">vectort.io</div>
        <div className="flex items-center space-x-8">
          <button onClick={() => navigate("/features")} className="hover:text-green-400 transition-colors">Features</button>
          <button onClick={() => navigate("/pricing")} className="hover:text-green-400 transition-colors">Pricing</button>
          <a href="#faqs" className="hover:text-green-400 transition-colors">FAQs</a>
          <Button 
            onClick={() => navigate("/auth")}
            className="bg-white text-black hover:bg-gray-200"
          >
            Get Started <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="flex flex-col lg:flex-row items-center justify-between px-8 py-20 min-h-[80vh]">
        {/* Left side - Auth & Content */}
        <div className="lg:w-1/2 space-y-8">
          {/* Trust indicator */}
          <div className="flex items-center space-x-2 text-sm text-gray-400 mb-8">
            <div className="flex -space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full border-2 border-black"></div>
              <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-400 rounded-full border-2 border-black"></div>
              <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-red-400 rounded-full border-2 border-black"></div>
            </div>
            <span>Trusted by {stats.users} Users</span>
          </div>

          {/* Floating logo */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-gray-400 to-gray-600 rounded-xl transform rotate-45 opacity-80"></div>
              <Star className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 -rotate-45 text-white h-8 w-8" />
            </div>
          </div>

          {/* Main heading */}
          <div className="text-center lg:text-left">
            <h1 className="text-6xl lg:text-7xl font-bold mb-4">
              Transform ideas into<br />
              <span className="text-green-400">AI-powered</span> applications
            </h1>
            
            <p className="text-gray-400 mb-8">
              Already have an account? 
              <button 
                onClick={() => navigate("/auth")}
                className="text-green-400 hover:underline ml-2"
              >
                Sign in
              </button>
            </p>
          </div>

          {/* Auth buttons */}
          <div className="space-y-4">
            <Button 
              onClick={() => navigate("/auth")}
              className="w-full bg-white text-black hover:bg-gray-200 py-6 text-lg font-medium"
            >
              <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </Button>

            <div className="flex space-x-4">
              <Button 
                onClick={() => navigate("/auth")}
                variant="outline" 
                className="flex-1 bg-transparent border-gray-700 text-white hover:bg-gray-900 py-6"
              >
                <svg className="mr-2 h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.477 2 2 6.59 2 12.253c0 4.53 2.865 8.373 6.839 9.728.5.093.683-.217.683-.489 0-.243-.009-1.051-.013-1.91-2.782.605-3.369-1.235-3.369-1.235-.454-1.184-1.11-1.499-1.11-1.499-.908-.634.069-.621.069-.621 1.004.072 1.533 1.056 1.533 1.056.892 1.568 2.341 1.115 2.91.853.09-.663.35-1.115.636-1.371-2.22-.253-4.555-1.132-4.555-5.04 0-1.113.39-2.028 1.03-2.744-.103-.253-.446-1.295.098-2.698 0 0 .84-.275 2.75 1.048A9.38 9.38 0 0112 6.958c.85.004 1.705.117 2.504.343 1.909-1.323 2.747-1.048 2.747-1.048.546 1.403.203 2.445.1 2.698.642.716 1.031 1.631 1.031 2.744 0 3.916-2.338 4.784-4.565 5.033.359.314.679.934.679 1.881 0 1.36-.012 2.457-.012 2.791 0 .274.18.586.688.486C19.137 20.622 22 16.78 22 12.253 22 6.59 17.523 2 12 2z"/>
                </svg>
                GitHub
              </Button>
              <Button 
                onClick={() => navigate("/auth")}
                variant="outline" 
                className="flex-1 bg-transparent border-gray-700 text-white hover:bg-gray-900 py-6"
              >
                <svg className="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.065 21.933c-1.176 1.14-2.459.96-3.695.49-1.308-.49-2.504-.514-3.867.49-1.726.842-2.635.622-3.655-.49C1.85 15.897 2.714 6.707 9.362 6.371c1.619.084 2.748.841 3.697.904 1.416-.269 2.771-.963 4.285-.822 1.818.142 3.183.83 4.049 2.441-3.744 2.241-2.856 7.147 1.256 9.002-.603 1.8-1.372 3.586-2.584 4.037zM12.042 6.299c-.118-2.677 2.153-4.878 4.636-4.799-.281 3.442-3.126 5.659-4.636 4.799z"/>
                </svg>
                Apple
              </Button>
            </div>

            <div className="text-center text-gray-500">Or start with email</div>

            <Button 
              onClick={() => navigate("/auth")}
              variant="outline" 
              className="w-full bg-transparent border-green-400 text-green-400 hover:bg-green-400 hover:text-black py-6 text-lg"
            >
              Sign up with Email
            </Button>

            <p className="text-xs text-gray-500 text-center">
              By continuing, you agree to our{" "}
              <a href="#" className="text-green-400 hover:underline">Terms of Service</a>{" "}
              and{" "}
              <a href="#" className="text-green-400 hover:underline">Privacy Policy</a>.
            </p>
          </div>
        </div>

        {/* Right side - App carousel */}
        <div className="lg:w-1/2 flex justify-center lg:justify-end mt-16 lg:mt-0">
          <div className="relative w-full max-w-lg">
            <div className="relative overflow-hidden rounded-2xl">
              <div 
                className="flex transition-transform duration-500 ease-in-out"
                style={{ transform: `translateX(-${currentSlide * 100}%)` }}
              >
                {demoApps.map((app, index) => (
                  <div key={index} className="w-full flex-shrink-0">
                    <Card className="bg-gray-900 border-gray-700 p-6">
                      <img 
                        src={app.image}
                        alt={app.title}
                        className="w-full h-64 object-cover rounded-lg mb-4"
                      />
                      <h3 className="text-xl font-semibold text-white mb-2">{app.title}</h3>
                      <p className="text-gray-400">{app.description}</p>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Navigation buttons */}
            <button 
              onClick={prevSlide}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 p-2 rounded-full transition-all"
            >
              <ArrowLeft className="h-5 w-5 text-white" />
            </button>
            <button 
              onClick={nextSlide}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 p-2 rounded-full transition-all"
            >
              <ArrowRight className="h-5 w-5 text-white" />
            </button>

            {/* Indicators */}
            <div className="flex justify-center mt-4 space-x-2">
              {demoApps.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    currentSlide === index ? "bg-green-400" : "bg-gray-600"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="flex justify-center items-center space-x-16 py-16 border-t border-gray-800">
        <div className="text-center">
          <div className="text-3xl font-bold text-green-400">{stats.users}</div>
          <div className="text-gray-400">Users</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-green-400">{stats.apps}</div>
          <div className="text-gray-400">Apps</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-green-400">{stats.countries}</div>
          <div className="text-gray-400">Countries</div>
        </div>
        <div className="text-center">
          <Badge variant="outline" className="border-orange-500 text-orange-500 px-4 py-2">
            YC
          </Badge>
          <div className="text-gray-400 mt-1">Backed by</div>
        </div>
      </div>

      {/* Meet Codex Section */}
      <div className="py-20 px-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-gray-400 to-gray-600 rounded-full flex items-center justify-center">
              <div className="w-12 h-12 bg-black rounded-full"></div>
            </div>
          </div>

          <h2 className="text-5xl font-bold mb-6">Meet Vectort</h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Vectort transforms concepts into production-ready applications with AI, 
            saving time and eliminating technical barriers.
          </p>

          {/* Build Interface */}
          <div className="max-w-2xl mx-auto">
            <VoiceTextarea
              placeholder="Décrivez ce que vous voulez construire... 🎤 Cliquez sur le micro pour parler"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full h-32 bg-gray-900 border-gray-700 text-white placeholder-gray-500 text-lg resize-none mb-6"
            />
            
            <Button 
              onClick={handleStartBuilding}
              disabled={!description.trim()}
              className="bg-white text-black hover:bg-gray-200 px-8 py-4 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Building <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Scroll indicator */}
          <div className="flex justify-center mt-20">
            <div className="flex items-center text-green-400">
              <ArrowDown className="h-5 w-5 mr-2 animate-bounce" />
              <span className="text-sm">Scroll down to see magic</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}