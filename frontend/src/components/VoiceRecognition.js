import React, { useState, useEffect, useContext, useRef } from 'react';
import { AppContext } from '../context/AppContext';
import { processVoiceCommand } from '../services/apiService';
import '../styles/components/VoiceRecognition.css';

const VoiceRecognition = () => {
  const { isListening, setIsListening, setCommand, setResponse } = useContext(AppContext);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);
  
  useEffect(() => {
    // Check if browser supports SpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setError('');
        console.log('Voice recognition started');
      };
      
      recognition.onresult = async (event) => {
        const currentTranscript = event.results[0][0].transcript;
        setTranscript(currentTranscript);
        
        // Check for wake word "TradeBot"
        if (currentTranscript.toLowerCase().includes('tradebot')) {
          const command = currentTranscript.toLowerCase().replace('tradebot', '').trim();
          if (command) {
            setCommand(command);
            await handleVoiceCommand(command);
          }
        }
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setError(`Error: ${event.error}`);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    } else {
      setError('Speech Recognition not supported in this browser');
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [setCommand, setIsListening]);

  // Toggle listening
  useEffect(() => {
    if (recognitionRef.current) {
      if (isListening) {
        recognitionRef.current.start();
      } else {
        recognitionRef.current.stop();
      }
    }
  }, [isListening]);

  const handleVoiceCommand = async (command) => {
    try {
      const data = await processVoiceCommand(command);
      setResponse(data.response);
      
      // Text-to-speech response
      const speech = new SpeechSynthesisUtterance(data.response);
      window.speechSynthesis.speak(speech);
    } catch (err) {
      console.error('Error processing voice command:', err);
      setResponse('Sorry, there was an error processing your command.');
    }
  };

  return (
    <div className="card voice-recognition-container">
      <div className="card-header">
        <h4>Voice Assistant</h4>
      </div>
      <div className="card-body text-center">
        <div className="voice-status">
          <div className={`status-indicator ${isListening ? 'active' : ''}`}></div>
          <span>{isListening ? 'Listening...' : 'Click to speak'}</span>
        </div>
        
        <button 
          className={`voice-button ${isListening ? 'listening' : ''}`} 
          onClick={() => setIsListening(!isListening)}
          disabled={!!error}
        >
          <i className="fa fa-microphone"></i>
        </button>
        
        {transcript && (
          <div className="transcript mt-3">
            <p><strong>You said:</strong> {transcript}</p>
          </div>
        )}
        
        {error && (
          <div className="alert alert-danger mt-3">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceRecognition;