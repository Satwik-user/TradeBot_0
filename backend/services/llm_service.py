import os
import logging
import requests
from openai import OpenAI

logger = logging.getLogger("tradebot.llm_service")

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.use_ollama = False if api_key else True

    async def generate_insight(self, symbol: str, timeframe: str, indicators: dict, patterns: list, analysis: dict) -> str:
        prompt = f"""
        You are a trading assistant. Simplify the technical analysis for {symbol} ({timeframe}).

        Indicators:
        RSI: {indicators.get('rsi')}
        MACD: {indicators.get('macd_data')}
        Bollinger Bands: {indicators.get('bollinger_bands')}
        Moving Averages: {indicators.get('moving_averages')}
        Volume SMA: {indicators.get('volume_sma')}

        Patterns Detected:
        {patterns}

        Raw Analysis:
        {analysis['analysis_text']}

        ❗ Task:
        - Summarize in **1-2 paragraphs**.
        - Explain trend in plain English.
        - Mention key risks/opportunities.
        - Give a confidence rating (low/medium/high).
        """

        # Try OpenAI first
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful trading assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.6
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI failed, falling back to Ollama: {e}")

        # Fallback → Ollama
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3.2:1b", "prompt": prompt, "stream": False}
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
            else:
                return f"⚠️ Ollama failed with {resp.text}"
        except Exception as e:
            logger.error(f"Ollama insight generation failed: {e}")
            return "⚠️ Unable to generate AI insight at this time."
