import { useState, useEffect, useRef } from 'react';

export const useSpeechToText = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Vérifier si le navigateur supporte la reconnaissance vocale
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      recognitionRef.current = new SpeechRecognition();
      
      const recognition = recognitionRef.current;
      recognition.continuous = false; // Changé à false pour éviter l'accumulation
      recognition.interimResults = true;
      recognition.lang = 'fr-FR'; // Français par défaut, peut être changé
      recognition.maxAlternatives = 1; // Une seule alternative pour éviter la confusion

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        // Parcourir TOUS les résultats depuis le début pour éviter l'accumulation
        for (let i = 0; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        // Mettre à jour UNIQUEMENT avec le nouveau contenu
        setTranscript(finalTranscript + interimTranscript);
      };

      recognition.onerror = (event) => {
        console.error('Erreur de reconnaissance vocale:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      try {
        // Vérifier l'état réel de la reconnaissance avant de démarrer
        if (recognitionRef.current.readyState === 1) {
          // Si déjà en cours, arrêter d'abord
          recognitionRef.current.stop();
          setTimeout(() => {
            if (!isListening) {
              recognitionRef.current.start();
            }
          }, 100);
        } else {
          recognitionRef.current.start();
        }
      } catch (error) {
        console.error('Erreur lors du démarrage de la reconnaissance:', error);
        if (error.name === 'InvalidStateError') {
          // Recognition déjà active, arrêter et redémarrer
          try {
            recognitionRef.current.stop();
            setTimeout(() => {
              if (!isListening && recognitionRef.current) {
                recognitionRef.current.start();
              }
            }, 200);
          } catch (retryError) {
            console.error('Impossible de redémarrer la reconnaissance:', retryError);
            setIsListening(false);
          }
        } else {
          setIsListening(false);
        }
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Erreur lors de l\'arrêt de la reconnaissance:', error);
        setIsListening(false);
      }
    }
  };

  const resetTranscript = () => {
    setTranscript('');
    if (recognitionRef.current && isListening) {
      stopListening();
    }
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