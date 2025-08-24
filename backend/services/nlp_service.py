import re
import logging
from typing import Tuple, Dict, Any, List
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Set up logger
logger = logging.getLogger("tradebot.nlp")

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Define patterns for different intents
INTENT_PATTERNS = {
    "market_query": [
        r"(?:what(?:'s| is)(?: the)? price(?: of)? (bitcoin|btc|ethereum|eth|dogecoin|doge))",
        r"(?:how (?:much|many) is|what(?:'s| is)(?: the)? value(?: of)?) (bitcoin|btc|ethereum|eth|dogecoin|doge)",
        r"(?:show|display|get)(?: me)?(?: the)? (bitcoin|btc|ethereum|eth|dogecoin|doge)(?:.*)(?:chart|price|value)",
        r"(?:current|latest) (?:price|value) (?:of|for) (bitcoin|btc|ethereum|eth|dogecoin|doge)"
    ],
    "trade_order": [
        r"(buy|sell) (\d+(?:\.\d+)?) (bitcoin|btc|ethereum|eth|dogecoin|doge)(?: at| when it hits| when it reaches)? ?(?:\$)?(\d+(?:\.\d+)?)?",
        r"(buy|sell) (bitcoin|btc|ethereum|eth|dogecoin|doge)(?: for| at| worth)? ?(?:\$)?(\d+(?:\.\d+)?)",
        r"place (?:a|an) (buy|sell) order for (\d+(?:\.\d+)?) (bitcoin|btc|ethereum|eth|dogecoin|doge)"
    ],
    "indicator_query": [
        r"(?:what(?:'s| is)(?: the)?) (rsi|macd|bollinger bands|moving average|ma)(?: for| of)? ?(bitcoin|btc|ethereum|eth|dogecoin|doge)?",
        r"(?:show|display|explain)(?: me)?(?: the)? (rsi|macd|bollinger bands|moving average|ma)(?: for| of)? ?(bitcoin|btc|ethereum|eth|dogecoin|doge)?",
        r"(?:explain|interpret|analyze)(?: the)? (rsi|macd|bollinger bands|moving average|ma)(?: indicator)?(?: for| of)? ?(bitcoin|btc|ethereum|eth|dogecoin|doge)?"
    ],
    "stop_loss": [
        r"(?:set|place|create)(?: a)? stop loss(?: at)? (\d+(?:\.\d+)?)%?(?: below(?: the)? entry| below(?: the)? current price)?(?: for (bitcoin|btc|ethereum|eth|dogecoin|doge))?",
        r"(?:set|place|create)(?: a)? (\d+(?:\.\d+)?)%? stop loss(?: for (bitcoin|btc|ethereum|eth|dogecoin|doge))?"
    ]
}

# Symbol mapping
SYMBOL_MAP = {
    "bitcoin": "BTCUSDT",
    "btc": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "eth": "ETHUSDT",
    "dogecoin": "DOGEUSDT",
    "doge": "DOGEUSDT"
}

def analyze_command(command: str) -> Tuple[str, Dict[str, Any]]:
    """
    Analyze a voice command to determine its intent and extract relevant entities
    
    Args:
        command (str): The voice command text
        
    Returns:
        Tuple[str, Dict[str, Any]]: The intent and extracted entities
    """
    command = command.lower().strip()
    
    # Check each intent pattern
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                entities = {}
                
                # Extract entities based on intent
                if intent == "market_query":
                    if len(match.groups()) > 0:
                        symbol = match.group(1)
                        entities["symbol"] = SYMBOL_MAP.get(symbol, "BTCUSDT")
                
                elif intent == "trade_order":
                    if len(match.groups()) >= 2:
                        entities["order_type"] = match.group(1)  # buy or sell
                        
                        # Check if quantity is numeric (pattern 1) or if it's a symbol (pattern 2)
                        if match.group(2) and re.match(r'\d+(?:\.\d+)?', match.group(2)):
                            entities["quantity"] = float(match.group(2))
                            entities["symbol"] = SYMBOL_MAP.get(match.group(3), "BTCUSDT")
                            if len(match.groups()) > 3 and match.group(4):
                                entities["price"] = float(match.group(4))
                        else:
                            entities["symbol"] = SYMBOL_MAP.get(match.group(2), "BTCUSDT")
                            if len(match.groups()) > 2 and match.group(3):
                                entities["price"] = float(match.group(3))
                                # For pattern 2, assume quantity of 1 if only price is provided
                                entities["quantity"] = 1.0
                
                elif intent == "indicator_query":
                    entities["indicator"] = match.group(1)
                    if len(match.groups()) > 1 and match.group(2):
                        entities["symbol"] = SYMBOL_MAP.get(match.group(2), "BTCUSDT")
                    else:
                        entities["symbol"] = "BTCUSDT"  # Default to BTC if no symbol specified
                
                elif intent == "stop_loss":
                    if intent == "stop_loss":
                        # Group 1 is always the percentage
                        entities["percentage"] = float(match.group(1))
                        # Group 2 may be the symbol, if provided
                        if len(match.groups()) > 1 and match.group(2):
                            entities["symbol"] = SYMBOL_MAP.get(match.group(2), "BTCUSDT")
                        else:
                            entities["symbol"] = "BTCUSDT"  # Default to BTC
                
                logger.info(f"Matched intent: {intent} with pattern: {pattern}")
                logger.info(f"Extracted entities: {entities}")
                return intent, entities
    
    # Basic intent classification for unmatched patterns
    tokens = word_tokenize(command)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]
    
    # Keywords for each intent
    market_keywords = ['price', 'value', 'worth', 'chart', 'market']
    trade_keywords = ['buy', 'sell', 'order', 'trade', 'execute']
    indicator_keywords = ['rsi', 'macd', 'indicator', 'bollinger', 'moving', 'average']
    stop_loss_keywords = ['stop', 'loss', 'limit']
    
    # Count keywords for each intent
    market_count = sum(1 for token in tokens if token.lower() in market_keywords)
    trade_count = sum(1 for token in tokens if token.lower() in trade_keywords)
    indicator_count = sum(1 for token in tokens if token.lower() in indicator_keywords)
    stop_loss_count = sum(1 for token in tokens if token.lower() in stop_loss_keywords)
    
    # Find the intent with the highest keyword count
    counts = {
        "market_query": market_count,
        "trade_order": trade_count,
        "indicator_query": indicator_count,
        "stop_loss": stop_loss_count
    }
    
    # Extract any potential symbols from the command
    entities = {}
    for keyword, symbol in SYMBOL_MAP.items():
        if keyword in command:
            entities["symbol"] = symbol
            break
    
    # If any count is greater than 0, use that intent
    max_count = max(counts.values())
    if max_count > 0:
        intent = max(counts, key=counts.get)
        logger.info(f"Fallback intent classification: {intent} with entities: {entities}")
        return intent, entities
    
    # Default to unknown intent if no patterns match and no keywords found
    return "unknown", {}