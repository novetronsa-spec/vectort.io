import { useState, useEffect, useRef } from 'react';

export const useSpeechToText = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);
  const isStartingRef = useRef(false);
  const isStoppingRef = useRef(false);

  useEffect(() => {
    // Vérifier si le navigateur supporte la reconnaissance vocale
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognition();
      
      const recognition = recognitionRef.current;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'fr-FR';
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        isStartingRef.current = false;
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        
        for (let i = 0; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          }
        }

        // Ne mettre à jour que s'il y a du contenu final
        if (finalTranscript.trim()) {
          setTranscript(finalTranscript.trim());
        }
      };

      recognition.onerror = (event) => {
        console.error('Erreur de reconnaissance vocale:', event.error);
        isStartingRef.current = false;
        isStoppingRef.current = false;
        setIsListening(false);
      };

      recognition.onend = () => {
        isStartingRef.current = false;
        isStoppingRef.current = false;
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          // Ignorer les erreurs de nettoyage
        }
      }
    };
  }, []);

  const startListening = () => {
    if (!recognitionRef.current || !isSupported || isStartingRef.current || isListening) {
      return;
    }

    isStartingRef.current = true;
    setTranscript('');
    
    // Attendre que tout soit propre avant de démarrer
    setTimeout(() => {
      try {
        if (recognitionRef.current && isStartingRef.current) {
          recognitionRef.current.start();
        }
      } catch (error) {
        console.error('Erreur lors du démarrage de la reconnaissance:', error);
        isStartingRef.current = false;
        setIsListening(false);
      }
    }, 50);
  };

  const stopListening = () => {
    if (!recognitionRef.current || !isListening || isStoppingRef.current) {
      return;
    }

    isStoppingRef.current = true;
    
    try {
      recognitionRef.current.stop();
    } catch (error) {
      console.error('Erreur lors de l\'arrêt de la reconnaissance:', error);
      isStoppingRef.current = false;
      setIsListening(false);
    }
  };

  const resetTranscript = () => {
    setTranscript('');
  };

  return {
    isListening,
    transcript,
    isSupported,
    startListening,
    stopListening,
    resetTranscript
  };
};