import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem("token"));

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
          const response = await axios.get(`${API}/auth/me`);
          setUser(response.data);
        } catch (error) {
          console.error("Auth initialization failed:", error);
          localStorage.removeItem("token");
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem("token", access_token);
      setToken(access_token);
      setUser(user);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || "Login failed" };
    }
  };

  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post(`${API}/auth/register`, { 
        email, 
        password, 
        full_name: fullName 
      });
      const { access_token, user } = response.data;
      
      localStorage.setItem("token", access_token);
      setToken(access_token);
      setUser(user);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      console.error("Registration error:", error.response?.data);
      
      // Gestion spécifique des erreurs de validation Pydantic
      let errorMessage = "Erreur lors de l'inscription";
      
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          // Erreurs de validation Pydantic
          const validationErrors = error.response.data.detail
            .map(err => err.msg || err.message)
            .join('. ');
          errorMessage = validationErrors;
        } else if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      }
      
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};