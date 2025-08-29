// frontend/src/components/VoiceRecognition.js
import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { processVoiceCommand } from '../services/apiService';

const VoiceRecognition = () => {
  const { state, actions } = useAppContext();
  const { isListening, command, response, user } = state;
  
  const [recognition, setRecognition] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();

      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        actions.setVoiceState({ isListening: true });
      };

      recognitionInstance.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Voice command received:', transcript);
        actions.setCommand(transcript);
        await handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        actions.setVoiceState({ 
          isListening: false, 
          response: `Voice recognition error: ${event.error}` 
        });
      };

      recognitionInstance.onend = () => {
        actions.setVoiceState({ isListening: false });
      };

      setRecognition(recognitionInstance);
      setIsSupported(true);
    } else {
      setIsSupported(false);
    }
  }, [actions]);

  const handleVoiceCommand = async (command) => {
    try {
      actions.setResponse('Processing your command...');

      const response = await processVoiceCommand(command);
      
      actions.setResponse(response.response);

      // Handle different actions based on backend response
      if (response.action === 'execute_trade' && response.data) {
        // Add trade to history for immediate visibility
        const tradeForHistory = {
          id: response.data.order_id,
          order_type: response.data.order_type,
          symbol: response.data.symbol,
          quantity: response.data.quantity,
          price: response.data.price,
          total_value: response.data.total_value,
          fee: response.data.fee,
          status: response.data.status,
          created_at: new Date().toISOString(),
          pair: { symbol: response.data.symbol }
        };
        
        actions.addTrade(tradeForHistory);
      }

      if (response.action === 'display_market_data' && response.data) {
        actions.updateMarketData({ [response.data.symbol]: response.data });
      }

      // Speak the response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.response);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      }

    } catch (error) {
      console.error('Error processing voice command:', error);
      const errorMessage = `Error: ${error.message}`;
      actions.setResponse(errorMessage);
    }
  };

  const startListening = () => {
    if (recognition && !isListening) {
      try {
        recognition.start();
      } catch (error) {
        console.error('Error starting recognition:', error);
        actions.setResponse('Error starting voice recognition');
      }
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  if (!isSupported) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <h5 className="card-title">🎤 Voice Assistant</h5>
          <div className="alert alert-warning">
            Voice recognition not supported in this browser.
            Please try Chrome, Edge, or Safari.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">🎤 Voice Assistant</h5>
        
        <div className="text-center mb-3">
          <button
            className={`btn ${isListening ? 'btn-danger' : 'btn-primary'} btn-lg`}
            onClick={isListening ? stopListening : startListening}
            disabled={!isSupported}
          >
            {isListening ? (
              <>
                <i className="fas fa-stop me-2"></i>
                Stop Listening
              </>
            ) : (
              <>
                <i className="fas fa-microphone me-2"></i>
                Start Listening
              </>
            )}
          </button>
          
          <div className={`mt-2 ${isListening ? 'text-danger' : 'text-muted'}`}>
            {isListening ? 'Listening...' : 'Click to speak'}
          </div>
        </div>

        <div className="voice-interaction">
          {command && (
            <div className="alert alert-info">
              <strong>You said:</strong> "{command}"
            </div>
          )}
          
          {response && (
            <div className="alert alert-success">
              <strong>TradeBot:</strong> {response}
            </div>
          )}
        </div>

        <div className="voice-help">
          <h6>Try saying:</h6>
          <ul className="list-unstyled small text-muted">
            <li>• "What's the price of Bitcoin?"</li>
            <li>• "Buy 0.1 Bitcoin"</li>
            <li>• "Show me RSI for Ethereum"</li>
            <li>• "Show my portfolio"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecognition;