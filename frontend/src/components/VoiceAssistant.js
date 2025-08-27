// src/components/VoiceAssistant.js
import React, { useState, useEffect } from 'react';

const VoiceAssistant = () => {
  const [isListening, setIsListening] = useState(false);
  const [lastCommand, setLastCommand] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();

      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        console.log('Voice recognition started');
        setIsListening(true);
      };

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Voice command received:', transcript);
        setLastCommand(transcript);
        handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setLastResponse(`Voice recognition error: ${event.error}`);
      };

      recognitionInstance.onend = () => {
        console.log('Voice recognition ended');
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    } else {
      console.log('Speech Recognition not supported');
    }
  }, []);

  const handleVoiceCommand = async (command) => {
    try {
      setLastResponse('Processing your command...');
      
      // Send command to backend
      console.log('Sending command to backend:', command);
      
      const response = await fetch('http://localhost:8000/api/voice/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: command }),
      });

      console.log('Backend response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response data:', data);
      
      setLastResponse(data.response);

      // Speak the response back
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.response);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        // Stop any ongoing speech
        window.speechSynthesis.cancel();
        
        // Speak the response
        window.speechSynthesis.speak(utterance);
        console.log('Speaking response:', data.response);
      }

    } catch (error) {
      console.error('Error processing voice command:', error);
      setLastResponse(`Error: ${error.message}`);
    }
  };

  const startListening = () => {
    if (recognition && !isListening) {
      try {
        recognition.start();
        console.log('Starting voice recognition...');
      } catch (error) {
        console.error('Error starting recognition:', error);
        setLastResponse('Error starting voice recognition');
      }
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
      console.log('Stopping voice recognition...');
    }
  };

  return (
    <div className="voice-assistant card">
      <h3>🎤 Voice Assistant</h3>
      
      <div className="voice-controls">
        <button
          className={`voice-btn ${isListening ? 'listening' : ''}`}
          onClick={isListening ? stopListening : startListening}
        >
          {isListening ? '🔴 Stop Listening' : '🎤 Start Listening'}
        </button>
      </div>

      <div className="voice-status">
        <div className={`status-indicator ${isListening ? 'active' : ''}`}>
          {isListening ? 'Listening...' : 'Click to speak'}
        </div>
      </div>

      <div className="voice-interaction">
        {lastCommand && (
          <div className="user-command">
            <strong>You said:</strong> "{lastCommand}"
          </div>
        )}
        
        {lastResponse && (
          <div className="bot-response">
            <strong>TradeBot:</strong> {lastResponse}
          </div>
        )}
      </div>

      <div className="voice-help">
        <p><strong>Try saying:</strong></p>
        <ul>
          <li>"What's the price of Bitcoin?"</li>
          <li>"Buy 0.1 Bitcoin"</li>
          <li>"Show me RSI for Bitcoin"</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceAssistant;