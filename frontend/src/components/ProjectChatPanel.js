import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Loader2, MessageSquare, Sparkles, Clock, CheckCircle2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ProjectChatPanel = ({ projectId, onCodeUpdated, userCredits }) => {
  const [messages, setMessages] = useState([]);
  const [iterations, setIterations] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChatHistory();
    loadIterations();
  }, [projectId]);

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

  const loadIterations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/projects/${projectId}/iterations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIterations(response.data.iterations || []);
    } catch (error) {
      console.error('Erreur chargement itérations:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Vérifier les crédits
    if (userCredits < 1) {
      alert('Crédits insuffisants! Vous avez besoin de 1 crédit pour améliorer votre projet.');
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Ajouter le message utilisateur immédiatement
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

      // Ajouter la réponse de l'assistant
      const assistantMsg = {
        role: 'assistant',
        content: response.data.explanation || 'Modifications appliquées avec succès!',
        timestamp: new Date().toISOString(),
        changes: response.data.changes_made || []
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Recharger les itérations
      await loadIterations();

      // Notifier le parent que le code a été mis à jour
      if (onCodeUpdated) {
        onCodeUpdated();
      }

      // Recharger les crédits
      window.location.reload(); // Simple refresh pour mettre à jour les crédits

    } catch (error) {
      console.error('Erreur envoi message:', error);
      const errorMsg = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Erreur lors du traitement de votre demande.',
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

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-900 rounded-lg">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-white">Chat IA - Amélioration Continue</h3>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span className="text-gray-400">{iterations.length} itérations</span>
          <span className="text-gray-600">•</span>
          <span className="text-gray-400">{userCredits} crédits</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <MessageSquare className="w-12 h-12 mb-4 text-gray-700" />
            <p className="text-lg font-medium">Commencez à améliorer votre projet</p>
            <p className="text-sm mt-2">Demandez des modifications, ajouts de fonctionnalités, ou corrections de bugs</p>
            <div className="mt-4 space-y-2 text-left bg-gray-800 p-4 rounded-lg">
              <p className="text-xs text-gray-400">💡 Exemples de commandes:</p>
              <p className="text-xs">• "Ajoute un formulaire de contact"</p>
              <p className="text-xs">• "Change la couleur du bouton en bleu"</p>
              <p className="text-xs">• "Ajoute une animation au chargement"</p>
              <p className="text-xs">• "Corrige le bug du menu mobile"</p>
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
                  className={`max-w-[80%] rounded-lg p-3 ${
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
                      
                      {/* Afficher les changements si présents */}
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
        <div className="flex gap-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Décrivez les améliorations souhaitées... (1 crédit par itération)"
            className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 ${
              isLoading || !inputMessage.trim()
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Amélioration...</span>
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
          💡 Coût: 1 crédit par amélioration • Appuyez sur Entrée pour envoyer
        </p>
      </div>
    </div>
  );
};

export default ProjectChatPanel;
