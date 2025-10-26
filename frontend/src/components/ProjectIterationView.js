import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Loader2, MessageSquare, Sparkles, Clock, CheckCircle2, Eye, Code2, Maximize2, AlertCircle, Info } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ProjectIterationView = ({ projectId, onClose, userCredits, onCreditsUpdated }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [previewHtml, setPreviewHtml] = useState('');
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [estimatedCredits, setEstimatedCredits] = useState(null);
  const [isEstimating, setIsEstimating] = useState(false);
  const [showPreview, setShowPreview] = useState(true);
  const messagesEndRef = useRef(null);
  const iframeRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChatHistory();
    loadPreview();
  }, [projectId]);

  // Estimate credits when user types
  useEffect(() => {
    if (inputMessage.trim().length > 10) {
      const timer = setTimeout(() => {
        estimateCredits(inputMessage);
      }, 800);
      return () => clearTimeout(timer);
    } else {
      setEstimatedCredits(null);
    }
  }, [inputMessage]);

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/projects/${projectId}/chat`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.messages || []);
      setIsLoadingHistory(false);
    } catch (error) {
      console.error('Erreur chargement historique chat:', error);
      setIsLoadingHistory(false);
    }
  };

  const loadPreview = async () => {
    setIsLoadingPreview(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/projects/${projectId}/preview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPreviewHtml(response.data);
    } catch (error) {
      console.error('Erreur chargement preview:', error);
      setPreviewHtml('<div style="color: white; padding: 20px;">Erreur lors du chargement du preview</div>');
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const estimateCredits = async (instruction) => {
    if (!instruction.trim()) return;
    
    setIsEstimating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/projects/${projectId}/estimate-credits`,
        { instruction },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setEstimatedCredits(response.data);
    } catch (error) {
      console.error('Erreur estimation crédits:', error);
      setEstimatedCredits(null);
    } finally {
      setIsEstimating(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setEstimatedCredits(null);

    // Add user message immediately
    const tempUserMsg = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/projects/${projectId}/iterate`,
        { instruction: userMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Add assistant response
      const assistantMsg = {
        role: 'assistant',
        content: response.data.explanation || 'Modifications appliquées avec succès!',
        timestamp: new Date().toISOString(),
        changes: response.data.changes_made || [],
        credits_used: response.data.credits_used || 1
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Reload preview to show changes
      await loadPreview();

      // Update credits
      if (onCreditsUpdated) {
        onCreditsUpdated();
      }

    } catch (error) {
      console.error('Erreur envoi message:', error);
      const errorDetail = error.response?.data?.detail || 'Erreur lors du traitement de votre demande.';
      const errorMsg = {
        role: 'assistant',
        content: errorDetail,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  const getComplexityColor = (level) => {
    const colors = {
      simple: 'text-green-400',
      medium: 'text-yellow-400',
      complex: 'text-orange-400',
      very_complex: 'text-red-400'
    };
    return colors[level] || 'text-gray-400';
  };

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-900 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-4">
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white px-3 py-1 rounded border border-gray-700 hover:border-gray-600"
          >
            ← Retour
          </button>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-white">Amélioration Continue</h2>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="flex items-center gap-2 px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300"
          >
            {showPreview ? <Code2 className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showPreview ? 'Masquer Preview' : 'Afficher Preview'}
          </button>
          <div className="flex items-center gap-2 text-sm px-3 py-1 rounded bg-gray-800">
            <Sparkles className="w-4 h-4 text-yellow-500" />
            <span className="text-gray-400">{userCredits} crédits</span>
          </div>
        </div>
      </div>

      {/* Main Content - Split Screen */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Chat */}
        <div className={`${showPreview ? 'w-1/2' : 'w-full'} flex flex-col border-r border-gray-800 bg-gray-900`}>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                <MessageSquare className="w-12 h-12 mb-4 text-gray-700" />
                <p className="text-lg font-medium">Commencez à améliorer votre projet</p>
                <p className="text-sm mt-2">Les crédits s'adaptent à la complexité de votre tâche</p>
                <div className="mt-4 space-y-2 text-left bg-gray-800 p-4 rounded-lg max-w-md">
                  <p className="text-xs text-gray-400">💡 Exemples:</p>
                  <p className="text-xs">• "Change la couleur en bleu" (1 crédit)</p>
                  <p className="text-xs">• "Ajoute un formulaire de contact" (2 crédits)</p>
                  <p className="text-xs">• "Intègre l'API Stripe" (3 crédits)</p>
                  <p className="text-xs">• "Refonte complète du design" (5 crédits)</p>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-lg p-3 ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : msg.isError
                          ? 'bg-red-900/30 text-red-400 border border-red-800'
                          : 'bg-gray-800 text-gray-200'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {msg.role === 'assistant' && !msg.isError && (
                          <Sparkles className="w-4 h-4 mt-1 text-blue-400 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          
                          {msg.changes && msg.changes.length > 0 && (
                            <div className="mt-2 pt-2 border-t border-gray-700">
                              <p className="text-xs text-gray-400 mb-1">✨ Modifications:</p>
                              <ul className="text-xs space-y-1">
                                {msg.changes.map((change, i) => (
                                  <li key={i} className="flex items-start gap-1">
                                    <CheckCircle2 className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                                    <span>{change}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {msg.credits_used && (
                            <div className="mt-2 text-xs text-blue-400">
                              💎 {msg.credits_used} crédit{msg.credits_used > 1 ? 's' : ''} utilisé{msg.credits_used > 1 ? 's' : ''}
                            </div>
                          )}
                          
                          <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatTimestamp(msg.timestamp)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-800 bg-gray-900">
            {/* Credit Estimation */}
            {estimatedCredits && (
              <div className={`mb-3 p-3 rounded-lg border ${
                estimatedCredits.has_enough_credits 
                  ? 'bg-blue-900/20 border-blue-800' 
                  : 'bg-red-900/20 border-red-800'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Info className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-gray-300">
                      Coût estimé: 
                      <span className={`font-bold ml-1 ${getComplexityColor(estimatedCredits.complexity_level)}`}>
                        {estimatedCredits.estimated_credits} crédit{estimatedCredits.estimated_credits > 1 ? 's' : ''}
                      </span>
                    </span>
                  </div>
                  <span className="text-xs text-gray-400 capitalize">
                    ({estimatedCredits.complexity_level})
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">{estimatedCredits.explanation}</p>
                {!estimatedCredits.has_enough_credits && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-red-400">
                    <AlertCircle className="w-3 h-3" />
                    Crédits insuffisants - Rechargez pour continuer
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Décrivez les améliorations souhaitées... (crédits adaptatifs)"
                className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim() || (estimatedCredits && !estimatedCredits.has_enough_credits)}
                className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 ${
                  isLoading || !inputMessage.trim() || (estimatedCredits && !estimatedCredits.has_enough_credits)
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>En cours...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Envoyer</span>
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              💡 Système adaptatif: 1-5 crédits selon la complexité • Entrée pour envoyer
            </p>
          </div>
        </div>

        {/* Right Panel - Live Preview */}
        {showPreview && (
          <div className="w-1/2 flex flex-col bg-gray-950">
            <div className="p-3 border-b border-gray-800 flex items-center justify-between bg-gray-900">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-300 font-medium">Preview en Temps Réel</span>
              </div>
              <button
                onClick={loadPreview}
                disabled={isLoadingPreview}
                className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-400 flex items-center gap-1"
              >
                {isLoadingPreview ? <Loader2 className="w-3 h-3 animate-spin" /> : '↻'}
                Actualiser
              </button>
            </div>
            <div className="flex-1 relative">
              {isLoadingPreview ? (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-950">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                </div>
              ) : (
                <iframe
                  ref={iframeRef}
                  srcDoc={previewHtml}
                  className="w-full h-full border-0"
                  sandbox="allow-scripts allow-same-origin"
                  title="Project Preview"
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectIterationView;
