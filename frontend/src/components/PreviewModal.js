import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Loader2, RefreshCw, Maximize2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const PreviewModal = ({ projectId, isOpen, onClose }) => {
  const [previewHtml, setPreviewHtml] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && projectId) {
      loadPreview();
    }
  }, [isOpen, projectId]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const loadPreview = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/projects/${projectId}/preview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPreviewHtml(response.data);
    } catch (err) {
      console.error('Erreur chargement preview:', err);
      setError(err.response?.data?.detail || 'Erreur lors du chargement du preview');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Maximize2 className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-semibold text-white">Prévisualisation du Projet</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadPreview}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualiser
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded hover:bg-gray-800 text-gray-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 relative bg-gray-950">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
              <p className="text-gray-400">Chargement du preview...</p>
            </div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center bg-red-900/20 border border-red-800 rounded-lg p-8 max-w-md">
              <p className="text-red-400 mb-4">{error}</p>
              <button
                onClick={loadPreview}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
              >
                Réessayer
              </button>
            </div>
          </div>
        ) : (
          <iframe
            srcDoc={previewHtml}
            className="w-full h-full border-0"
            sandbox="allow-scripts allow-same-origin allow-forms"
            title="Project Preview"
          />
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2 bg-gray-900 border-t border-gray-800 text-center">
        <p className="text-xs text-gray-500">
          💡 Appuyez sur Échap pour fermer • Utilisez le bouton 💬 pour améliorer le projet
        </p>
      </div>
    </div>
  );
};

export default PreviewModal;
