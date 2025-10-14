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
  useEffect(() => {
    if (transcript) {
      const newValue = currentValue + (currentValue ? ' ' : '') + transcript;
      setCurrentValue(newValue);
      if (onChange) {
        onChange({ target: { value: newValue, name: props.name } });
      }
    }
  }, [transcript, currentValue, onChange, props.name]);

  const handleTextChange = (e) => {
    const newValue = e.target.value;
    setCurrentValue(newValue);
    if (onChange) {
      onChange(e);
    }
  };

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening();
    }
  };

  const handleClearVoice = () => {
    resetTranscript();
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
              disabled={disabled}
              className={cn(
                "h-8 w-8 p-1",
                isListening 
                  ? "text-red-500 hover:text-red-600 bg-red-50 hover:bg-red-100" 
                  : "text-gray-500 hover:text-green-600"
              )}
              title={isListening ? "Arrêter l'enregistrement" : "Commencer l'enregistrement vocal"}
            >
              {isListening ? (
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
        <div className="absolute -bottom-6 left-0 right-0">
          <div className="flex items-center justify-center space-x-2 text-xs text-green-600">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span>Écoute en cours... Parlez maintenant</span>
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
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