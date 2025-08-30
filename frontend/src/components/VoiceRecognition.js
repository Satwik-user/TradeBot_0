// frontend/src/components/VoiceRecognition.js
import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '../context/AppContext';
import { processVoiceCommand } from '../services/apiService';

const VoiceRecognition = () => {
  const { state, actions } = useAppContext();
  const { isListening, command, response, user } = state;
  
  const [recognition, setRecognition] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('Ready');
  
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setDebugInfo('✅ Speech Recognition supported');
      
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';
      recognitionInstance.maxAlternatives = 1;

      recognitionInstance.onstart = () => {
        console.log('🎤 Speech recognition started');
        setDebugInfo('🎤 Listening...');
        actions.setVoiceState({ isListening: true });
        setError('');
      };

      recognitionInstance.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        const confidence = event.results[0][0].confidence;
        
        console.log('🗣️ Voice input:', transcript, 'Confidence:', confidence);
        setDebugInfo(`Heard: "${transcript}" (${Math.round(confidence * 100)}% confidence)`);
        
        actions.setCommand(transcript);
        await handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event) => {
        console.error('❌ Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
        setDebugInfo(`❌ Error: ${event.error}`);
        actions.setVoiceState({ isListening: false });
      };

      recognitionInstance.onend = () => {
        console.log('🛑 Speech recognition ended');
        actions.setVoiceState({ isListening: false });
        if (!error) {
          setDebugInfo('Ready to listen');
        }
      };

      setRecognition(recognitionInstance);
      recognitionRef.current = recognitionInstance;
      setIsSupported(true);
    } else {
      setIsSupported(false);
      setError('Speech Recognition not supported in this browser');
      setDebugInfo('❌ Speech Recognition not supported. Try Chrome, Edge, or Safari.');
    }
  }, [actions]);

  const handleVoiceCommand = async (command) => {
    try {
      setDebugInfo('🤔 Processing command...');
      actions.setResponse('Processing your command...');

      console.log('📤 Sending command to backend:', command);
      
      const response = await processVoiceCommand(command);
      
      console.log('📥 Backend response:', response);
      setDebugInfo('✅ Command processed successfully');
      
      actions.setResponse(response.response);

      // Handle different actions
      if (response.action === 'execute_trade' && response.data) {
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
        console.log('📊 Trade added to history:', tradeForHistory);
      }

      if (response.action === 'display_market_data' && response.data) {
        actions.updateMarketData({ [response.data.symbol]: response.data });
        console.log('💹 Market data updated:', response.data);
      }

      // Text-to-speech response
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.response);
        utterance.rate = 0.8;
        utterance.pitch = 1;
        utterance.volume = 1;
        
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        console.log('🔊 Speaking response');
      }

    } catch (error) {
      console.error('❌ Error processing voice command:', error);
      
      // ✅ FIXED: Properly handle error message
      let errorMessage = 'Failed to process command';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          if (Array.isArray(error.response.data.detail)) {
            errorMessage = error.response.data.detail.map(e => e.msg || e).join(', ');
          } else {
            errorMessage = error.response.data.detail;
          }
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      actions.setResponse(`Error: ${errorMessage}`);
      setError(errorMessage);
      setDebugInfo('❌ Processing failed');
    }
  };

  const startListening = async () => {
    if (!isSupported) {
      setError('Speech recognition not supported');
      return;
    }

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setDebugInfo('🎤 Microphone access granted');
      
      if (recognition && !isListening) {
        recognition.start();
        console.log('▶️ Starting speech recognition');
      }
    } catch (err) {
      console.error('❌ Microphone access denied:', err);
      setError('Microphone access denied. Please allow microphone access and try again.');
      setDebugInfo('❌ Microphone access denied');
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
      console.log('⏸️ Stopping speech recognition');
    }
  };

  // Manual text input for testing
  const [manualInput, setManualInput] = useState('');
  
  const handleManualSubmit = async (e) => {
    e.preventDefault();
    if (manualInput.trim()) {
      actions.setCommand(manualInput);
      await handleVoiceCommand(manualInput);
      setManualInput('');
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">🎤 Voice Assistant</h5>
        
        {/* Debug Info */}
        <div className="alert alert-info small mb-3">
          <strong>Status:</strong> {String(debugInfo)}
        </div>
        
        {/* ✅ FIXED: Error Display */}
        {error && (
          <div className="alert alert-danger">
            {String(error)}
          </div>
        )}
        
        {/* Voice Controls */}
        <div className="text-center mb-3">
          <button
            className={`btn ${isListening ? 'btn-danger' : 'btn-primary'} btn-lg me-2`}
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
          
          {isListening && (
            <div className="mt-2">
              <div className="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
              <span className="text-primary">Listening for your command...</span>
            </div>
          )}
        </div>

        {/* Manual Input for Testing */}
        <form onSubmit={handleManualSubmit} className="mb-3">
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Type command for testing (e.g., 'buy 0.1 bitcoin')"
              value={manualInput}
              onChange={(e) => setManualInput(e.target.value)}
            />
            <button type="submit" className="btn btn-outline-secondary">
              <i className="fas fa-paper-plane me-1"></i>
              Test
            </button>
          </div>
        </form>

        {/* Command Display */}
        {command && (
          <div className="alert alert-info">
            <strong>You said:</strong> "{String(command)}"
          </div>
        )}
        
        {/* ✅ FIXED: Response Display */}
        {response && (
          <div className="alert alert-success">
            <strong>TradeBot:</strong> {String(response)}
          </div>
        )}

        {/* Help Section */}
        <div className="voice-help">
          <h6>Try saying:</h6>
          <ul className="list-unstyled small text-muted">
            <li>• "Buy 0.1 Bitcoin"</li>
            <li>• "What's the price of Ethereum?"</li>
            <li>• "Show me RSI for Dogecoin"</li>
            <li>• "Purchase 1000 Dogecoin"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VoiceRecognition;