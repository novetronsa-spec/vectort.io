/**
 * OAuth Helper Functions
 * Gère les flux d'authentification OAuth pour Google, GitHub et Apple
 */

const API_URL = process.env.REACT_APP_BACKEND_URL || 'https://vectort-builder.preview.emergentagent.com';

/**
 * Initie le flux OAuth Google
 */
export const loginWithGoogle = () => {
  // Redirige directement vers l'endpoint backend qui génère l'URL d'autorisation
  window.location.href = `${API_URL}/api/auth/google/login`;
};

/**
 * Initie le flux OAuth GitHub
 */
export const loginWithGitHub = () => {
  // Redirige directement vers l'endpoint backend qui génère l'URL d'autorisation
  window.location.href = `${API_URL}/api/auth/github/login`;
};

/**
 * Initie le flux OAuth Apple
 */
export const loginWithApple = () => {
  // Redirige directement vers l'endpoint backend qui génère l'URL d'autorisation
  window.location.href = `${API_URL}/api/auth/apple/login`;
};

/**
 * Gère le callback OAuth après authentification
 * Extrait le token de l'URL et le stocke dans localStorage
 */
export const handleOAuthCallback = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get('token');
  const provider = urlParams.get('provider');

  if (token) {
    // Stocke le token dans localStorage
    localStorage.setItem('token', token);
    localStorage.setItem('oauth_provider', provider || 'unknown');
    
    // Nettoie l'URL
    window.history.replaceState({}, document.title, window.location.pathname);
    
    return { token, provider };
  }

  return null;
};
