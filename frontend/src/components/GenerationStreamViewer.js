import React, { useState, useEffect, useRef } from 'react';
import './GenerationStreamViewer.css';

/**
 * GenerationStreamViewer - Affiche la progression en temps réel comme Emergent
 * 
 * Features:
 * - Server-Sent Events (SSE) pour streaming
 * - Affichage messages des agents en direct
 * - Liste des fichiers créés
 * - Barre de progression
 * - Auto-scroll
 */
const GenerationStreamViewer = ({ projectId, onComplete }) => {
  const [messages, setMessages] = useState([]);
  const [filesCreated, setFilesCreated] = useState([]);
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('Initialisation...');
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  // Auto-scroll vers le bas
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!projectId) return;

    // Créer connexion SSE
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    const token = localStorage.getItem('token');
    
    // EventSource ne supporte pas custom headers, donc on passe le token en query param
    const url = `${backendUrl}/api/projects/${projectId}/stream?token=${token}`;
    
    console.log('📡 Connexion SSE:', url);
    
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('✅ Connexion SSE établie');
      addMessage('info', '📡 Connexion établie - En attente de génération...');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleStreamMessage(data);
      } catch (err) {
        console.error('❌ Erreur parse message:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('❌ Erreur SSE:', err);
      if (eventSource.readyState === EventSource.CLOSED) {
        setError('Connexion perdue. Rechargez la page.');
        addMessage('error', '❌ Connexion perdue');
      }
    };

    // Nettoyage
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [projectId]);

  const handleStreamMessage = (data) => {
    const { type, content, agent, file_path, progress: newProgress, metadata } = data;

    // Mettre à jour progression
    if (newProgress !== undefined) {
      setProgress(newProgress);
    }

    // Ajouter message
    addMessage(type, content, agent);

    // Gérer types spécifiques
    switch (type) {
      case 'phase':
        setPhase(content);
        break;
      
      case 'file_created':
        if (file_path && !filesCreated.includes(file_path)) {
          setFilesCreated(prev => [...prev, file_path]);
        }
        break;
      
      case 'complete':
        setIsComplete(true);
        setProgress(100);
        if (onComplete) {
          onComplete();
        }
        break;
      
      case 'error':
        setError(content);
        break;
      
      default:
        break;
    }
  };

  const addMessage = (type, content, agent = null) => {
    const message = {
      id: Date.now() + Math.random(),
      type,
      content,
      agent,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, message]);
  };

  const getMessageIcon = (type) => {
    const icons = {
      'info': '🤖',
      'phase': '🔄',
      'success': '✅',
      'file_created': '📄',
      'error': '❌',
      'complete': '🎉'
    };
    return icons[type] || '•';
  };

  const getMessageClass = (type) => {
    return `message message-${type}`;
  };

  return (
    <div className="generation-stream-viewer">
      {/* Header avec progression */}
      <div className="stream-header">
        <div className="stream-title">
          <span className="pulse-dot"></span>
          {isComplete ? '✅ Génération terminée' : `${phase}`}
        </div>
        
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          >
            <span className="progress-text">{progress}%</span>
          </div>
        </div>
      </div>

      <div className="stream-content">
        {/* Messages en direct */}
        <div className="messages-panel">
          <div className="panel-title">📋 Journal de génération</div>
          <div className="messages-list">
            {messages.map(msg => (
              <div key={msg.id} className={getMessageClass(msg.type)}>
                <span className="message-icon">{getMessageIcon(msg.type)}</span>
                <span className="message-time">{msg.timestamp}</span>
                {msg.agent && <span className="message-agent">[{msg.agent}]</span>}
                <span className="message-content">{msg.content}</span>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Fichiers créés */}
        <div className="files-panel">
          <div className="panel-title">📁 Fichiers créés ({filesCreated.length})</div>
          <div className="files-list">
            {filesCreated.map((file, idx) => (
              <div key={idx} className="file-item">
                <span className="file-icon">📄</span>
                <span className="file-path">{file}</span>
              </div>
            ))}
            {filesCreated.length === 0 && (
              <div className="no-files">Aucun fichier créé pour le moment...</div>
            )}
          </div>
        </div>
      </div>

      {/* Erreur */}
      {error && (
        <div className="stream-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {/* Completion */}
      {isComplete && (
        <div className="stream-complete">
          <div className="complete-icon">🎉</div>
          <div className="complete-text">
            Génération terminée avec succès !
            <br />
            <small>{filesCreated.length} fichiers créés</small>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerationStreamViewer;
