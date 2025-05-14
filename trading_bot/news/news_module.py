import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from ..config.settings import settings
from ..ai.gemini_interface import GeminiInterface

logger = logging.getLogger(__name__)

class NewsModule:
    def __init__(self):
        """Initialize the news module with API keys and Gemini interface."""
        self.news_api_key = settings.THE_NEWS_API_TOKEN
        self.gemini = GeminiInterface()
        self.base_url = "https://api.thenewsapi.com/v1"
        
    def fetch_news(self, keywords: List[str], categories: List[str] = ["business", "tech"]) -> List[Dict]:
        print("[DEBUG] Fetching news from The News API...")
        try:
            # Calculate time range (last 24 hours)
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=24)
            
            # Comprehensive financial and crypto keywords
            base_keywords = [
                # I. General Market & Economic Terms
                "stock market", "market trends", "economic outlook", "inflation", "deflation", "interest rates",
                "federal reserve", "ECB", "Bank of England", "GDP", "unemployment rate", "consumer spending",
                "retail sales", "manufacturing PMI", "services PMI", "trade deficit", "trade surplus", "fiscal policy",
                "monetary policy", "recession", "economic recovery", "bull market", "bear market", "market volatility",
                "VIX", "Dow Jones", "DJIA", "S&P 500", "Nasdaq", "FTSE 100", "DAX", "Nikkei 225", "global economy",
                "emerging markets",
                # II. Cryptocurrency Specific
                "bitcoin", "BTC", "ethereum", "ETH", "cryptocurrency", "blockchain", "DeFi", "NFT", "altcoin",
                "crypto regulation", "crypto mining", "binance news", "coinbase news", "wallet", "halving", "staking",
                "ICO", "IDO", "Web3", "metaverse", "CBDC", "stablecoin", "USDT", "USDC", "crypto adoption",
                # III. Company & Earnings Related
                "earnings report", "quarterly results", "profit warning", "revenue growth", "stock split", "dividend",
                "IPO", "SPAC", "mergers and acquisitions", "M&A", "share buyback", "AAPL", "MSFT", "TSLA", "Apple news",
                "Tesla news", "CEO change", "product launch", "analyst rating", "price target", "investor call",
                "shareholder meeting", "market capitalization", "enterprise value",
                # IV. Commodities & Forex
                "oil price", "WTI", "Brent", "gold price", "silver price", "commodities", "forex", "USD", "EUR", "JPY",
                "GBP", "currency exchange rates", "OPEC",
                # V. Investment & Trading Terms
                "investment strategy", "portfolio management", "asset allocation", "hedge fund", "mutual fund", "ETF",
                "bonds", "treasury bonds", "corporate bonds", "yield curve", "short selling", "options trading",
                "futures contract", "risk management", "technical analysis", "fundamental analysis", "arbitrage",
                # VI. Other Financial Events & Concepts
                "geopolitical risk", "supply chain", "cybersecurity", "fintech",
                # Exchanges
                "Binance", "Coinbase", "Kraken", "Bybit", "OKX",
                # Key Projects/Foundations
                "Ripple", "XRP", "Solana Foundation", "Cardano Foundation", "Polkadot", "Web3 Foundation",
                # Prominent Figures in Crypto
                "Changpeng Zhao", "CZ", "Brian Armstrong", "Vitalik Buterin", "Michael Saylor",
                # Regulatory Bodies & Government Agencies
                "SEC", "U.S. Securities and Exchange Commission", "CFTC", "U.S. Commodity Futures Trading Commission",
                "Federal Reserve", "The Fed", "U.S. Treasury Department", "ESMA", "European Securities and Markets Authority",
                "FCA", "UK Financial Conduct Authority",
                # International Organizations
                "IMF", "International Monetary Fund", "World Bank", "OPEC", "Organization of the Petroleum Exporting Countries",
                "WEF", "World Economic Forum", "G7", "G20",
                # Trump & Sanctions Related
                "Trump sanctions", "Donald Trump sanctions", "Trump administration sanctions", "Sanctions under Trump",
                "Trump Iran sanctions", "Trump China sanctions", "Trump Russia sanctions", "Trump North Korea sanctions",
                "Trump Venezuela sanctions", "US sanctions Trump", "Trump trade war", "Trump tariffs", "Donald Trump economy",
                "Trump policy", "Trump financial news", "Trump China trade", "Economic sanctions", "Trade sanctions",
                "Financial sanctions", "US sanctions", "New sanctions", "Sanctions lifted", "Sanctions imposed",
                "Impact of sanctions"
            ]
            # Merge and deduplicate keywords
            search_keywords = list(set(base_keywords + [k.lower() for k in keywords]))
            
            # Prepare query parameters
            params = {
                "api_token": self.news_api_key,
                "search": " OR ".join(search_keywords),
                "categories": ",".join(categories),
                "language": "en",
                "published_after": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "published_before": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "limit": 10  # Limit to 10 most relevant articles
            }
            print(f"[DEBUG] News API params: {params}")
            
            # Make initial API request to get base articles
            response = requests.get(f"{self.base_url}/news/all", params=params, timeout=10)
            response.raise_for_status()
            print("[DEBUG] News API base articles fetched.")
            
            # Flatten articles from all categories if needed
            data = response.json().get("data", [])
            articles = []
            if isinstance(data, dict):
                for category_articles in data.values():
                    articles.extend(category_articles)
            elif isinstance(data, list):
                articles = data
            print(f"[DEBUG] Number of base articles: {len(articles)}")
            
            # For each base article, get similar articles
            for idx, article in enumerate(articles):
                print(f"[DEBUG] Processing base article {idx+1}/{len(articles)}: {article.get('title')}")
                # Add the base article
                articles.append({
                    "uuid": article.get("uuid"),
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "snippet": article.get("snippet"),
                    "url": article.get("url"),
                    "published_at": article.get("published_at"),
                    "source": article.get("source"),
                    "relevance_score": article.get("relevance_score", 0)
                })
                
                # Get similar articles
                similar_params = {
                    "api_token": self.news_api_key,
                    "language": "en",
                    "categories": ",".join(categories),
                    "limit": 3  # Get 3 similar articles per base article
                }
                
                try:
                    similar_response = requests.get(
                        f"{self.base_url}/news/similar/{article.get('uuid')}",
                        params=similar_params,
                        timeout=10
                    )
                    similar_response.raise_for_status()
                    print(f"[DEBUG] Similar articles fetched for base article {article.get('uuid')}")
                    
                    # Add similar articles
                    for similar in similar_response.json().get("data", []):
                        if similar.get("uuid") != article.get("uuid"):  # Avoid duplicates
                            articles.append({
                                "uuid": similar.get("uuid"),
                                "title": similar.get("title"),
                                "description": similar.get("description"),
                                "snippet": similar.get("snippet"),
                                "url": similar.get("url"),
                                "published_at": similar.get("published_at"),
                                "source": similar.get("source"),
                                "relevance_score": similar.get("relevance_score", 0)
                            })
                except Exception as e:
                    logger.warning(f"Error fetching similar articles: {str(e)}")
                    print(f"[DEBUG] Error fetching similar articles: {str(e)}")
                    continue
            
            # Sort articles by relevance score
            articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    unique_articles.append(article)
            print(f"[DEBUG] Returning {len(unique_articles[:10])} unique articles.")
            return unique_articles[:10]  # Return top 10 most relevant articles
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            print(f"[DEBUG] Error fetching news: {str(e)}")
            return []
            
    def analyze_news(self, article: Dict, target_asset: str) -> Dict:
        print(f"[DEBUG] Analyzing news article for {target_asset}: {article.get('title')}")
        try:
            # Prepare the prompt for Gemini with a timeout
            prompt = f"""
            Analyze this news article for {target_asset} trading impact. Be concise.

            Title: {article['title']}
            Description: {article['description']}
            Source: {article['source']}
            Published: {article['published_at']}

            Return ONLY a JSON object in this exact format:
            {{
                "signal": "BUY/SELL/HOLD",
                "confidence_score": <float between 0 and 1>,
                "rationale": "<1-2 sentences>",
                "trading_pair": "{target_asset}",
                "news_source": "{article['source']}",
                "news_title": "{article['title']}",
                "published_at": "{article['published_at']}"
            }}
            """
            
            # Get analysis from Gemini with a timeout
            try:
                print(f"[DEBUG] Sending prompt to Gemini for article: {article.get('title')}")
                response = self.gemini.model.generate_content(prompt)
                print(f"[DEBUG] Gemini response received for: {article.get('title')}")
                response_text = response.text.strip()
                
                # Try to extract JSON from the response
                try:
                    # First try direct JSON parsing
                    analysis = json.loads(response_text)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from the text
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        logger.error(f"Failed to extract JSON from response: {response_text}")
                        print(f"[DEBUG] Failed to extract JSON from response: {response_text}")
                        return None
                
                # Validate the analysis
                required_fields = ["signal", "confidence_score", "rationale", "trading_pair"]
                if not all(field in analysis for field in required_fields):
                    logger.error(f"Missing required fields in analysis: {analysis}")
                    print(f"[DEBUG] Missing required fields in analysis: {analysis}")
                    return None
                
                # Ensure signal is valid
                if analysis["signal"] not in ["BUY", "SELL", "HOLD"]:
                    logger.error(f"Invalid signal in analysis: {analysis['signal']}")
                    print(f"[DEBUG] Invalid signal in analysis: {analysis['signal']}")
                    return None
                
                # Ensure confidence score is valid
                try:
                    confidence = float(analysis["confidence_score"])
                    if not 0 <= confidence <= 1:
                        logger.error(f"Invalid confidence score: {confidence}")
                        print(f"[DEBUG] Invalid confidence score: {confidence}")
                        return None
                    analysis["confidence_score"] = confidence
                except (ValueError, TypeError):
                    logger.error(f"Invalid confidence score format: {analysis['confidence_score']}")
                    print(f"[DEBUG] Invalid confidence score format: {analysis['confidence_score']}")
                    return None
                
                return analysis
                
            except Exception as e:
                logger.error(f"Error getting Gemini response: {str(e)}")
                print(f"[DEBUG] Error getting Gemini response: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing news: {str(e)}")
            print(f"[DEBUG] Error analyzing news: {str(e)}")
            return None
            
    def get_news_signals(self, trading_pairs: List[str]) -> List[Dict]:
        print(f"[DEBUG] Getting news signals for trading pairs: {trading_pairs}")
        signals = []
        
        try:
            # Generate keywords based on trading pairs
            keywords = []
            for pair in trading_pairs:
                base = pair[:-4]  # Remove USDT
                keywords.extend([
                    f"{base} price",
                    f"{base} news",
                    f"{base} update",
                    f"{base} analysis"
                ])
            
            # Fetch relevant news
            articles = self.fetch_news(keywords)
            print(f"[DEBUG] Number of articles to analyze: {len(articles)}")
            
            if not articles:
                logger.warning("No relevant news articles found")
                print("[DEBUG] No relevant news articles found")
                return []
            
            # Analyze only the first 3 articles for testing
            for idx, article in enumerate(articles[:3]):
                print(f"[DEBUG] Analyzing article {idx+1}/{min(3, len(articles))}: {article.get('title')}")
                for pair in trading_pairs:
                    base = pair[:-4].lower()
                    if (base in article['title'].lower() or 
                        base in article['description'].lower() or 
                        base in article.get('snippet', '').lower()):
                        analysis = self.analyze_news(article, pair)
                        if analysis:
                            signals.append(analysis)
                            # Break after finding a match for this pair
                            break
            print(f"[DEBUG] Total signals generated: {len(signals)}")
            return signals
            
        except Exception as e:
            logger.error(f"Error getting news signals: {str(e)}")
            print(f"[DEBUG] Error getting news signals: {str(e)}")
            return [] 