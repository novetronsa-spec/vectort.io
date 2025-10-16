import React, { useState, useEffect, useRef } from 'react';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Mic, MicOff, Volume2, Paperclip, Github, GitFork, Zap, X, Upload, FileText } from 'lucide-react';
import { useSpeechToText } from '../hooks/useSpeechToText';
import { cn } from '../lib/utils';

const VoiceTextarea = ({ 
  value, 
  onChange, 
  placeholder, 
  className,
  disabled = false,
  onFileUpload,
  onGithubSave,
  onFork,
  onUltraMode,
  showAdvancedTools = false,
  ...props 
}) => {
  const { 
    isListening, 
    transcript, 
    isSupported, 
    startListening, 
    stopListening, 
    resetTranscript 
  } = useSpeechToText();
  
  const [currentValue, setCurrentValue] = useState(value || '');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUltraMode, setIsUltraMode] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // Synchroniser avec la valeur externe
  useEffect(() => {
    if (value !== undefined) {
      setCurrentValue(value);
    }
  }, [value]);

  // Mettre à jour le texte avec la reconnaissance vocale
  const [lastTranscript, setLastTranscript] = useState('');
  const [voiceTextAdded, setVoiceTextAdded] = useState(false);
  
  useEffect(() => {
    if (transcript && transcript.trim()) {
      // Si c'est un nouveau transcript et pas une répétition
      if (transcript !== lastTranscript) {
        let newValue = currentValue;
        
        // Si on avait déjà ajouté du texte vocal, le remplacer
        if (voiceTextAdded && lastTranscript && currentValue.includes(lastTranscript)) {
          newValue = currentValue.replace(lastTranscript, transcript);
        } else {
          // Ajouter le nouveau transcript
          newValue = currentValue + (currentValue && !currentValue.endsWith(' ') ? ' ' : '') + transcript;
        }
        
        setCurrentValue(newValue);
        setLastTranscript(transcript);
        setVoiceTextAdded(true);
        
        if (onChange) {
          onChange({ target: { value: newValue, name: props.name } });
        }
      }
    }
  }, [transcript]);

  const handleTextChange = (e) => {
    const newValue = e.target.value;
    setCurrentValue(newValue);
    if (onChange) {
      onChange(e);
    }
  };

  const [isProcessing, setIsProcessing] = useState(false);
  
  const handleMicClick = () => {
    // Prévenir les clics multiples rapides
    if (isProcessing) {
      return;
    }
    
    setIsProcessing(true);
    
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      setLastTranscript('');
      setVoiceTextAdded(false);
      startListening();
    }
    
    // Débloquer après un délai
    setTimeout(() => {
      setIsProcessing(false);
    }, 300);
  };

  const handleClearVoice = () => {
    resetTranscript();
    setLastTranscript('');
    setVoiceTextAdded(false);
    stopListening();
  };

  // Gestion de l'upload de fichiers
  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files]);
      if (onFileUpload) {
        onFileUpload(files);
      }
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Gestion de GitHub Save
  const handleGithubSave = () => {
    if (onGithubSave) {
      onGithubSave(currentValue, uploadedFiles);
    }
  };

  // Gestion de Fork
  const handleFork = () => {
    if (onFork) {
      onFork(currentValue);
    }
  };

  // Gestion du mode Ultra
  const handleUltraToggle = () => {
    const newUltraMode = !isUltraMode;
    setIsUltraMode(newUltraMode);
    if (onUltraMode) {
      onUltraMode(newUltraMode);
    }
  };

  return (
    <div className="relative">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileChange}
        accept=".txt,.md,.json,.js,.jsx,.ts,.tsx,.py,.html,.css,.pdf,.doc,.docx"
      />
      
      <Textarea
        ref={textareaRef}
        value={currentValue}
        onChange={handleTextChange}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          "resize-none",
          isListening && "border-green-500 ring-1 ring-green-500",
          isUltraMode && "border-purple-500 ring-2 ring-purple-500 bg-purple-900/10",
          className
        )}
        {...props}
      />
      
      {/* Barre d'outils EN DESSOUS */}
      <div className="flex items-center justify-between mt-3 px-2 py-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center space-x-3">
          {/* Bouton Upload de fichiers */}
          {showAdvancedTools && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleFileClick}
              disabled={disabled}
              className="h-10 px-3 text-gray-400 hover:text-blue-500 hover:bg-blue-950 flex items-center space-x-2"
              title="Attacher des fichiers"
            >
              <Paperclip className="h-5 w-5" />
              <span className="text-sm">Fichiers</span>
            </Button>
          )}

          {/* Bouton GitHub Save */}
          {showAdvancedTools && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleGithubSave}
              disabled={disabled || !currentValue.trim()}
              className="h-10 px-3 text-gray-400 hover:text-gray-100 hover:bg-gray-700 flex items-center space-x-2"
              title="Save to GitHub"
            >
              <Github className="h-5 w-5" />
              <span className="text-sm">GitHub</span>
            </Button>
          )}

          {/* Bouton Fork */}
          {showAdvancedTools && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleFork}
              disabled={disabled || !currentValue.trim()}
              className="h-10 px-3 text-gray-400 hover:text-orange-500 hover:bg-orange-950 flex items-center space-x-2"
              title="Fork ce projet"
            >
              <GitFork className="h-5 w-5" />
              <span className="text-sm">Fork</span>
            </Button>
          )}

          {/* Bouton Ultra Mode */}
          {showAdvancedTools && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleUltraToggle}
              disabled={disabled}
              className={cn(
                "h-10 px-3 flex items-center space-x-2",
                isUltraMode 
                  ? "text-purple-400 hover:text-purple-300 bg-purple-900/30 hover:bg-purple-900/50" 
                  : "text-gray-400 hover:text-purple-400 hover:bg-purple-950"
              )}
              title={isUltraMode ? "Désactiver le mode Ultra" : "Activer le mode Ultra"}
            >
              <Zap className={cn("h-5 w-5", isUltraMode && "animate-pulse")} />
              <span className="text-sm font-medium">Ultra</span>
            </Button>
          )}
        </div>
        
        {/* Boutons de contrôle vocal à droite */}
        <div className="flex items-center space-x-2">
          {isSupported ? (
            <>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleMicClick}
                disabled={disabled || isProcessing}
                className={cn(
                  "h-10 px-3 flex items-center space-x-2",
                  isListening 
                    ? "text-red-500 hover:text-red-400 bg-red-900/30 hover:bg-red-900/50" 
                    : "text-gray-400 hover:text-green-500 hover:bg-green-950",
                  isProcessing && "opacity-50 cursor-not-allowed"
                )}
                title={
                  isProcessing ? "Traitement en cours..." :
                  isListening ? "Arrêter l'enregistrement" : "Commencer l'enregistrement vocal"
                }
              >
                {isProcessing ? (
                  <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                ) : isListening ? (
                  <MicOff className="h-5 w-5 animate-pulse" />
                ) : (
                  <Mic className="h-5 w-5" />
                )}
                <span className="text-sm">{isListening ? "Arrêter" : "Micro"}</span>
              </Button>
              
              {/* Bouton pour effacer le transcript vocal */}
              {transcript && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleClearVoice}
                  className="h-10 px-3 text-gray-400 hover:text-orange-500 hover:bg-orange-950 flex items-center space-x-2"
                  title="Effacer l'enregistrement vocal"
                >
                  <Volume2 className="h-5 w-5" />
                  <span className="text-sm">Effacer</span>
                </Button>
              )}
            </>
          ) : (
            <div 
              className="h-10 px-3 flex items-center justify-center text-gray-500 text-sm"
              title="Reconnaissance vocale non supportée par ce navigateur"
            >
              <MicOff className="h-4 w-4 mr-2" />
              Non supporté
            </div>
          )}
        </div>
      </div>

      {/* Liste des fichiers uploadés */}
      {uploadedFiles.length > 0 && (
        <div className="mt-3 space-y-2">
          <div className="text-xs text-gray-400 font-medium mb-1">Fichiers attachés :</div>
          {uploadedFiles.map((file, index) => (
            <div 
              key={index} 
              className="flex items-center justify-between bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm hover:border-gray-600 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-blue-400 flex-shrink-0" />
                <div>
                  <div className="text-gray-200 font-medium">{file.name}</div>
                  <div className="text-gray-500 text-xs">
                    {(file.size / 1024).toFixed(1)} KB
                  </div>
                </div>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
                className="h-8 w-8 p-0 text-gray-500 hover:text-red-500 hover:bg-red-950"
                title="Supprimer ce fichier"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Indicateur Mode Ultra */}
      {isUltraMode && (
        <div className="mt-3">
          <div className="flex items-center justify-center space-x-2 text-sm text-purple-300 bg-purple-900/30 rounded-lg py-3 px-4 border border-purple-600">
            <Zap className="h-5 w-5 animate-pulse" />
            <span className="font-medium">⚡ Mode Ultra Activé - Génération maximale avec toutes les optimisations</span>
          </div>
        </div>
      )}

      {/* Indicateur d'état vocal */}
      {isListening && !isUltraMode && (
        <div className="mt-3">
          <div className="flex items-center justify-center space-x-3 text-sm text-green-300 bg-green-900/30 rounded-lg py-3 px-4 border border-green-600">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
            </div>
            <span className="font-medium">🎤 Écoute active - Parlez maintenant...</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.3s'}}></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
            </div>
          </div>
        </div>
      )}

      {/* Affichage du transcript en cours */}
      {transcript && !isListening && !isUltraMode && (
        <div className="mt-2">
          <div className="text-xs text-gray-400 bg-gray-800 rounded px-3 py-2 border border-gray-700">
            <span className="font-medium text-gray-300">Transcrit:</span> {transcript.substring(0, 100)}...
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceTextarea;