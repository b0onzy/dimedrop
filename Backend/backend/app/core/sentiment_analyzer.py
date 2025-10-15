# DimeDrop Sentiment Analyzer
# Analyzes market sentiment from Reddit and News sources to generate Flip Score

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from fastapi import HTTPException
import httpx
import praw
import logging
from textblob import TextBlob
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        # Check if APIs are configured with real credentials (not placeholders)
        reddit_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
        news_key = os.getenv('NEWSAPI_KEY')
        
        # Check if credentials look like real values (not placeholders)
        self.reddit_available = (
            reddit_id and reddit_secret and
            not reddit_id.startswith('placeholder') and
            not reddit_secret.startswith('placeholder') and
            len(reddit_id) > 10 and len(reddit_secret) > 10
        )
        
        self.news_api_available = (
            news_key and
            not news_key.startswith('placeholder') and
            len(news_key) > 10
        )
        
        if self.reddit_available:
            # Initialize PRAW for Reddit API
            self.reddit = praw.Reddit(
                client_id=reddit_id,
                client_secret=reddit_secret,
                user_agent='DimeDrop/1.0 by DimeDropBot'
            )
        else:
            self.reddit = None
            logger.warning("Reddit API not configured with real credentials - using mock data")
        
        # NewsAPI for basketball-related news
        self.news_api_key = news_key
        self.news_base_url = 'https://newsapi.org/v2/'
        
        # Weighting factors for sentiment calculation
        self.redditor_weight = 0.3  # Higher karma = more weight
        self.post_age_weight = 0.2  # Newer posts = more weight
        self.sentiment_confidence = 0.5  # Base confidence multiplier
        
        # Cache settings
        self.cache_duration = timedelta(hours=6)  # 6-hour cache for sentiment

    async def analyze_card_sentiment(self, card_name: str) -> Dict:
        """
        Analyzes sentiment for a basketball card from multiple sources
        Returns a comprehensive sentiment report with Flip Score
        """
        try:
            # Fetch data from all sources
            reddit_data = await self._fetch_reddit_sentiment(card_name)
            news_data = await self._fetch_news_sentiment(card_name)
            
            # Calculate composite sentiment
            composite_sentiment = self._calculate_composite_sentiment(
                reddit_data, news_data, card_name
            )
            
            # Generate Flip Score
            flip_score = self._calculate_flip_score(composite_sentiment, card_name)
            
            # Compile results
            result = {
                'card_name': card_name,
                'timestamp': datetime.now(),
                'flip_score': flip_score,
                'sentiment_breakdown': composite_sentiment,
                'total_discussions': reddit_data['total_posts'] + news_data['total_articles'],
                'last_updated': datetime.now(),
                'confidence_level': 'high' if composite_sentiment['total_sources'] > 2 else 'medium'
            }
            
            logger.info(f"Sentiment analysis complete for '{card_name}', Flip Score: {flip_score}")
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            raise HTTPException(status_code=500, detail="Error performing sentiment analysis")

    async def _fetch_reddit_sentiment(self, card_name: str) -> Dict:
        """
        Fetch sentiment data from relevant Reddit communities
        """
        # Return mock data if Reddit API not configured
        if not self.reddit_available:
            logger.info(f"Using mock Reddit data for '{card_name}' (API not configured)")
            return {
                'total_posts': 3,
                'avg_sentiment': 0.65,  # Slightly positive sentiment
                'posts': [
                    {'title': f'Hot take on {card_name}', 'score': 25, 'num_comments': 8},
                    {'title': f'{card_name} market analysis', 'score': 15, 'num_comments': 5},
                    {'title': f'Just picked up {card_name}', 'score': 8, 'num_comments': 3}
                ],
                'sentiment_scores': [0.7, 0.6, 0.65],
                'source': 'reddit_mock'
            }
        
        # Real Reddit API code
        try:
            # Define target subreddits
            target_subreddits = ['sports', 'basketballcards', 'tradingcards', 'sportscollectors', 'nba']
            
            all_posts = []
            total_posts = 0
            
            # Search in each subreddit
            for subreddit_name in target_subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts = subreddit.search(card_name, sort='new', limit=10)
                    
                    for post in posts:
                        # Get post details
                        post_age = datetime.now() - datetime.fromtimestamp(post.created_utc)
                        post_data = {
                            'title': post.title,
                            'selftext': post.selftext,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': post.created_utc,
                            'subreddit': post.subreddit.display_name,
                            'author_karma': self._get_author_karma(post.author),
                            'post_age_hours': post_age.total_seconds() / 3600
                        }
                        all_posts.append(post_data)
                        total_posts += 1
                except Exception as e:
                    logger.warning(f"Error fetching posts from /r/{subreddit_name}: {str(e)}")
                    continue
            
            # Analyze sentiment of each post
            sentiment_scores = []
            for post in all_posts:
                text = f"{post['title']} {post['selftext']}"
                if len(text.strip()) > 0:  # Only analyze non-empty posts
                    sentiment_score = self._analyze_text_sentiment(text)
                    sentiment_scores.append({
                        'score': sentiment_score,
                        'weight': self._calculate_post_weight(post),
                        'post': post
                    })
            
            # Calculate weighted average sentiment
            weighted_sentiment = 0
            total_weight = 0
            
            for item in sentiment_scores:
                weighted_sentiment += item['score'] * item['weight']
                total_weight += item['weight']
            
            avg_sentiment = weighted_sentiment / total_weight if total_weight > 0 else 0
            
            return {
                'total_posts': total_posts,
                'avg_sentiment': avg_sentiment,
                'posts': all_posts,
                'sentiment_scores': [s['score'] for s in sentiment_scores],
                'source': 'reddit'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Reddit sentiment: {str(e)}")
            return {
                'total_posts': 0,
                'avg_sentiment': 0,
                'posts': [],
                'sentiment_scores': [],
                'source': 'reddit'
            }

    async def _fetch_news_sentiment(self, card_name: str) -> Dict:
        """
        Fetch sentiment from news articles using NewsAPI
        """
        try:
            if not self.news_api_key:
                logger.warning("NewsAPI key not configured, skipping news sentiment")
                return {
                    'total_articles': 0,
                    'avg_sentiment': 0,
                    'articles': [],
                    'sentiment_scores': [],
                    'source': 'news'
                }
            
            # Construct search query
            query = f"basketball card {card_name}"
            
            # Request to NewsAPI
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 20
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.news_base_url}everything",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    # Analyze sentiment for each article
                    sentiment_scores = []
                    processed_articles = []
                    
                    for article in articles:
                        title = article.get('title', '') or ''
                        description = article.get('description', '') or ''
                        content = article.get('content', '') or ''
                        
                        text = f"{title} {description} {content}"
                        
                        if text.strip():
                            sentiment_score = self._analyze_text_sentiment(text)
                            
                            article_data = {
                                'title': title,
                                'description': description,
                                'url': article.get('url', ''),
                                'published_at': article.get('publishedAt'),
                                'source': article.get('source', {}).get('name', 'Unknown')
                            }
                            
                            sentiment_scores.append(sentiment_score)
                            processed_articles.append(article_data)
                    
                    # Calculate average sentiment
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                    
                    return {
                        'total_articles': len(articles),
                        'avg_sentiment': avg_sentiment,
                        'articles': processed_articles,
                        'sentiment_scores': sentiment_scores,
                        'source': 'news'
                    }
                else:
                    logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
                    return {
                        'total_articles': 0,
                        'avg_sentiment': 0,
                        'articles': [],
                        'sentiment_scores': [],
                        'source': 'news'
                    }
        
        except Exception as e:
            logger.error(f"Error fetching news sentiment: {str(e)}")
            return {
                'total_articles': 0,
                'avg_sentiment': 0,
                'articles': [],
                'sentiment_scores': [],
                'source': 'news'
            }

    def _calculate_post_weight(self, post: Dict) -> float:
        """
        Calculate the weight of a Reddit post based on various factors
        """
        # Base weight
        weight = 1.0
        
        # Weight by karma of author (capped to prevent extreme weights)
        if post['author_karma']:
            weight += min(post['author_karma'] / 1000, 2.0)  # Max 2 additional weight from karma
        
        # Weight by post score (upvotes)
        weight += min(post['score'] / 50, 1.0)  # Max 1 additional weight from score
        
        # Weight by recency (newer posts have higher weight)
        max_age_hours = 168  # 1 week
        age_factor = 1 - (post['post_age_hours'] / max_age_hours)
        age_factor = max(age_factor, 0.1)  # Minimum age factor
        weight *= age_factor
        
        return weight

    def _get_author_karma(self, author) -> Optional[int]:
        """
        Get author's post karma (with error handling)
        """
        try:
            if author:
                return author.comment_karma + author.link_karma
            return None
        except:
            return None  # Return None if we can't get karma

    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using TextBlob
        Returns polarity score between -1 (negative) and 1 (positive)
        """
        if not text or not text.strip():
            return 0.0
        
        try:
            # Clean text
            cleaned_text = re.sub(r'http\S+', '', text)  # Remove URLs
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
            
            # Analyze sentiment
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            
            # Ensure the result is within [-1, 1]
            return max(min(polarity, 1.0), -1.0)
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {str(e)}, text: {text[:100]}...")
            return 0.0

    def _calculate_composite_sentiment(self, reddit_data: Dict, news_data: Dict, card_name: str) -> Dict:
        """
        Combine Reddit and News sentiment data into a single analysis
        """
        # Calculate weighted composite sentiment
        reddit_weight = 0.7  # Reddit has higher weight as it's more relevant to collectors
        news_weight = 0.3    # News provides context but less specific to cards
        
        reddit_sentiment = reddit_data['avg_sentiment']
        news_sentiment = news_data['avg_sentiment']
        
        composite_sentiment = (
            reddit_sentiment * reddit_weight +
            news_sentiment * news_weight
        )
        
        return {
            'overall_sentiment': composite_sentiment,
            'reddit_sentiment': reddit_sentiment,
            'news_sentiment': news_sentiment,
            'reddit_weight': reddit_weight,
            'news_weight': news_weight,
            'total_sources': (reddit_data['total_posts'] > 0) + (news_data['total_articles'] > 0),
            'reddit_confidence': min(reddit_data['total_posts'] / 10, 1.0),  # Max confidence 1.0
            'news_confidence': min(news_data['total_articles'] / 5, 1.0),    # Max confidence 1.0
        }

    def _calculate_flip_score(self, composite_sentiment: Dict, card_name: str) -> int:
        """
        Calculate the Flip Score (0-100) based on sentiment and other factors
        """
        # Base sentiment score (convert from -1/1 to 0/100 scale)
        base_sentiment = (composite_sentiment['overall_sentiment'] + 1) * 50
        
        # Adjust for confidence
        reddit_conf = composite_sentiment['reddit_confidence']
        news_conf = composite_sentiment['news_confidence']
        avg_confidence = (reddit_conf + news_conf) / 2
        
        # Calculate final score
        score = base_sentiment * avg_confidence
        
        # Additional factors can be added here in the future
        # For example, we might consider the volume of discussions
        total_discussions = composite_sentiment['reddit_sentiment'] * 10  # Placeholder
        
        # Ensure score is between 0 and 100
        final_score = max(0, min(100, int(score)))
        
        return final_score


# Global instance for use in FastAPI
sentiment_analyzer = SentimentAnalyzer()


# Example usage for testing
if __name__ == "__main__":
    # This would be used for testing the module independently
    import asyncio
    
    async def test_analyzer():
        # Mock environment variables for testing
        os.environ['REDDIT_CLIENT_ID'] = 'test_client_id'
        os.environ['REDDIT_CLIENT_SECRET'] = 'test_client_secret'
        os.environ['NEWS_API_KEY'] = 'test_news_key'
        
        analyzer = SentimentAnalyzer()
        try:
            # Test with a common card
            results = await analyzer.analyze_card_sentiment("wembanyama rookie")
            print(f"Flip Score: {results['flip_score']}")
            print(f"Sentiment Breakdown: {results['sentiment_breakdown']}")
        except Exception as e:
            print(f"Test failed: {str(e)}")
    
    asyncio.run(test_analyzer())