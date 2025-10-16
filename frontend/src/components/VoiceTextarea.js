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
          "pr-24", // Espace pour les boutons
          isListening && "border-green-500 ring-1 ring-green-500",
          isUltraMode && "border-purple-500 ring-2 ring-purple-500 bg-purple-900/10",
          className
        )}
        {...props}
      />
      
      {/* Barre d'outils principale */}
      <div className="absolute right-2 top-2 flex items-center space-x-1">
        {/* Bouton Upload de fichiers */}
        {showAdvancedTools && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleFileClick}
            disabled={disabled}
            className="h-8 w-8 p-1 text-gray-500 hover:text-blue-600"
            title="Attacher des fichiers"
          >
            <Paperclip className="h-4 w-4" />
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
            className="h-8 w-8 p-1 text-gray-500 hover:text-gray-900 dark:hover:text-white"
            title="Save to GitHub"
          >
            <Github className="h-4 w-4" />
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
            className="h-8 w-8 p-1 text-gray-500 hover:text-orange-600"
            title="Fork ce projet"
          >
            <GitFork className="h-4 w-4" />
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
              "h-8 w-8 p-1",
              isUltraMode 
                ? "text-purple-500 hover:text-purple-600 bg-purple-50 dark:bg-purple-900/30" 
                : "text-gray-500 hover:text-purple-600"
            )}
            title={isUltraMode ? "Désactiver le mode Ultra" : "Activer le mode Ultra"}
          >
            <Zap className={cn("h-4 w-4", isUltraMode && "animate-pulse")} />
          </Button>
        )}
        
        {/* Boutons de contrôle vocal */}
        {isSupported ? (
          <>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleMicClick}
              disabled={disabled || isProcessing}
              className={cn(
                "h-8 w-8 p-1",
                isListening 
                  ? "text-red-500 hover:text-red-600 bg-red-50 dark:bg-red-900/30 hover:bg-red-100" 
                  : "text-gray-500 hover:text-green-600",
                isProcessing && "opacity-50 cursor-not-allowed"
              )}
              title={
                isProcessing ? "Traitement en cours..." :
                isListening ? "Arrêter l'enregistrement" : "Commencer l'enregistrement vocal"
              }
            >
              {isProcessing ? (
                <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
              ) : isListening ? (
                <MicOff className="h-4 w-4 animate-pulse" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </Button>
            
            {/* Bouton pour effacer le transcript vocal */}
            {transcript && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleClearVoice}
                className="h-8 w-8 p-1 text-gray-500 hover:text-orange-600"
                title="Effacer l'enregistrement vocal"
              >
                <Volume2 className="h-4 w-4" />
              </Button>
            )}
          </>
        ) : (
          <div 
            className="h-8 w-8 p-1 flex items-center justify-center text-gray-400 text-xs"
            title="Reconnaissance vocale non supportée par ce navigateur"
          >
            <MicOff className="h-3 w-3" />
          </div>
        )}
      </div>

      {/* Liste des fichiers uploadés */}
      {uploadedFiles.length > 0 && (
        <div className="mt-2 space-y-1">
          {uploadedFiles.map((file, index) => (
            <div 
              key={index} 
              className="flex items-center justify-between bg-gray-100 dark:bg-gray-800 rounded px-3 py-2 text-sm"
            >
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-blue-500" />
                <span className="text-gray-700 dark:text-gray-300">{file.name}</span>
                <span className="text-gray-500 text-xs">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
                className="h-6 w-6 p-0 text-gray-500 hover:text-red-600"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Indicateur Mode Ultra */}
      {isUltraMode && (
        <div className="absolute -bottom-8 left-0 right-0">
          <div className="flex items-center justify-center space-x-2 text-sm text-purple-400 bg-purple-50 dark:bg-purple-900/30 rounded-lg py-2 px-4 border border-purple-200 dark:border-purple-700">
            <Zap className="h-4 w-4 animate-pulse" />
            <span className="font-medium">⚡ Mode Ultra Activé - Génération maximale</span>
          </div>
        </div>
      )}

      {/* Indicateur d'état vocal */}
      {isListening && !isUltraMode && (
        <div className="absolute -bottom-8 left-0 right-0">
          <div className="flex items-center justify-center space-x-3 text-sm text-green-400 bg-green-50 dark:bg-green-900/30 rounded-lg py-2 px-4 border border-green-200 dark:border-green-700">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
            </div>
            <span className="font-medium">🎤 Écoute active - Parlez maintenant...</span>
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.3s'}}></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
            </div>
          </div>
        </div>
      )}

      {/* Affichage du transcript en cours */}
      {transcript && !isListening && !isUltraMode && (
        <div className="absolute -bottom-6 left-0 right-0">
          <div className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 rounded px-2 py-1">
            <span className="font-medium">Transcrit:</span> {transcript.substring(0, 50)}...
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceTextarea;