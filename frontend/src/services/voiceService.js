// Text-to-speech functionality
export const speakText = (text) => {
  if ('speechSynthesis' in window) {
    // Create a new speech synthesis utterance
    const speech = new SpeechSynthesisUtterance(text);
    
    // Configure speech settings
    speech.lang = 'en-US';
    speech.volume = 1; // 0 to 1
    speech.rate = 1;   // 0.1 to 10
    speech.pitch = 1;  // 0 to 2
    
    // Speak the text
    window.speechSynthesis.speak(speech);
    
    return true;
  } else {
    console.error('Speech synthesis not supported in this browser');
    return false;
  }
};

// Get available voices
export const getVoices = () => {
  if ('speechSynthesis' in window) {
    return window.speechSynthesis.getVoices();
  }
  return [];
};

// Check if speech synthesis is supported
export const isSpeechSynthesisSupported = () => {
  return 'speechSynthesis' in window;
};

// Check if speech recognition is supported
export const isSpeechRecognitionSupported = () => {
  return window.SpeechRecognition || window.webkitSpeechRecognition;
};