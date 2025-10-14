import React, { useState, useEffect, useRef } from 'react';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { useSpeechToText } from '../hooks/useSpeechToText';
import { cn } from '../lib/utils';

const VoiceTextarea = ({ 
  value, 
  onChange, 
  placeholder, 
  className,
  disabled = false,
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

  return (
    <div className="relative">
      <Textarea
        ref={textareaRef}
        value={currentValue}
        onChange={handleTextChange}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          "pr-24", // Espace pour les boutons
          isListening && "border-green-500 ring-1 ring-green-500",
          className
        )}
        {...props}
      />
      
      {/* Boutons de contrôle vocal */}
      <div className="absolute right-2 top-2 flex space-x-1">
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
                  ? "text-red-500 hover:text-red-600 bg-red-50 hover:bg-red-100" 
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

      {/* Indicateur d'état vocal */}
      {isListening && (
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
      {transcript && !isListening && (
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