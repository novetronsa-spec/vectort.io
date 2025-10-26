import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { handleOAuthCallback } from '../utils/oauth';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const processCallback = () => {
      try {
        const result = handleOAuthCallback();
        
        if (result && result.token) {
          // Authentification réussie, redirige vers le dashboard
          console.log(`✅ Authentification ${result.provider} réussie`);
          setTimeout(() => {
            navigate('/dashboard');
          }, 500);
        } else {
          // Pas de token, redirige vers la page d'accueil
          console.error('❌ Pas de token OAuth trouvé');
          navigate('/');
        }
      } catch (error) {
        console.error('❌ Erreur lors du traitement du callback OAuth:', error);
        navigate('/');
      }
    };

    processCallback();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-400 mb-4"></div>
        <h2 className="text-white text-xl">Authentification en cours...</h2>
        <p className="text-gray-400 mt-2">Veuillez patienter</p>
      </div>
    </div>
  );
};

export default AuthCallback;
