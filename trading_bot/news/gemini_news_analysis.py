import datetime
import logging
from typing import List, Dict, Optional
from ..config.settings import settings
from ..ai.gemini_interface import GeminiInterface

logger = logging.getLogger(__name__)

class GeminiNewsAndAnalysisModule:
    def __init__(self):
        self.gemini = GeminiInterface()
        self.last_news = None
        self.last_analysis = None

    def discover_news(self, focus: str = "crypto market", date: Optional[str] = None) -> List[Dict]:
        """
        Use Gemini to discover and summarize the top news for a given focus and date.
        Returns a list of news items (headline/summary, source/context if available).
        """
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        prompt = (
            f"Act as an expert financial news aggregator. "
            f"Scan for and provide a concise summary of the top 3-5 most impactful financial and cryptocurrency news items for today, {date}. "
            f"Focus on news relevant to {focus}. For each item, provide a brief headline or summary, and if possible, the perceived source or context. "
            f"Prioritize information that could influence trading decisions."
        )
        try:
            response = self.gemini.model.generate_content(prompt)
            news_items = self._parse_news_list(response.text)
            self.last_news = news_items
            return news_items
        except Exception as e:
            logger.error(f"Error discovering news with Gemini: {e}")
            return []

    def analyze_news(self, news_items: List[Dict], target_asset: str = "BTC/USD") -> Dict:
        """
        Use Gemini to analyze the discovered news and generate a trading signal and sentiment.
        Returns a dict with sentiment, signal, confidence, and justification.
        """
        news_summary = "\n".join(
            [f"- {item.get('headline', item.get('summary', str(item)))}" for item in news_items]
        )
        prompt = (
            f"You are an expert financial and crypto market analyst. Based on the following news items:\n"
            f"{news_summary}\n\n"
            f"Now, for {target_asset}, please:\n"
            f"1. Analyze the overall market sentiment (Bullish, Bearish, Neutral, Uncertain).\n"
            f"2. Provide a potential trading signal: BUY, SELL, or HOLD for {target_asset}.\n"
            f"3. Assign a confidence score: Low, Medium, or High.\n"
            f"4. Briefly (1-2 sentences) explain your reasoning, referencing specific news."
        )
        try:
            response = self.gemini.model.generate_content(prompt)
            analysis = self._parse_analysis(response.text)
            self.last_analysis = analysis
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing news with Gemini: {e}")
            return {}

    def run_discovery_and_analysis(self, focus: str = "crypto market", target_asset: str = "BTC/USD") -> Dict:
        """
        Runs both discovery and analysis in sequence and returns the final analysis.
        """
        news = self.discover_news(focus=focus)
        if not news:
            return {"error": "No news found"}
        analysis = self.analyze_news(news, target_asset=target_asset)
        return {
            "news": news,
            "analysis": analysis
        }

    def _parse_news_list(self, text: str) -> List[Dict]:
        # Simple parser: expects bullet points or numbered list from Gemini
        lines = [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
        news_items = [{"headline": line} for line in lines if line]
        return news_items

    def _parse_analysis(self, text: str) -> Dict:
        # Simple parser: look for keywords in Gemini's response
        result = {}
        for line in text.split('\n'):
            l = line.lower()
            if "sentiment" in l:
                result["sentiment"] = line.split(":")[-1].strip().capitalize()
            elif "signal" in l:
                result["signal"] = line.split(":")[-1].strip().upper()
            elif "confidence" in l:
                result["confidence"] = line.split(":")[-1].strip().capitalize()
            elif "reason" in l or "because" in l:
                result["justification"] = line.strip()
        if not result:
            result["raw"] = text
        return result 