"""
Social Media Posting Module
Handles automated daily posts to Twitter/X, LinkedIn with trading metrics.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Optional: Install tweepy for Twitter integration
# Optional: Install linkedin-api for LinkedIn integration
# For now, provide templates and logging

logger = logging.getLogger(__name__)


class SocialPoster:
    """
    Posts daily trading metrics to social media platforms.
    Currently supports template generation and logging.
    Can be extended with tweepy/linkedin-api integrations.
    """

    def __init__(self):
        """Initialize social poster with optional API credentials."""
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_profile_id = os.getenv("LINKEDIN_PROFILE_ID")

        self.enable_twitter = bool(self.twitter_bearer_token)
        self.enable_linkedin = bool(self.linkedin_access_token)

        logger.info(
            f"SocialPoster initialized - Twitter: {self.enable_twitter}, LinkedIn: {self.enable_linkedin}"
        )

    def generate_daily_update_post(
        self,
        pnl: float,
        pnl_percent: float,
        win_rate: float,
        trade_count: int,
        sharpe_ratio: float,
        validation_score: float,
        reputation_score: float,
        leaderboard_rank: Optional[int] = None,
    ) -> str:
        """
        Generate a tweet-length (280 char) social media post.

        Args:
            pnl: Profit/loss in USD
            pnl_percent: PnL percentage
            win_rate: Win rate (0-1)
            trade_count: Number of trades
            sharpe_ratio: Sharpe ratio
            validation_score: Validation score (0-100)
            reputation_score: Reputation score (0-100)
            leaderboard_rank: Current leaderboard ranking

        Returns:
            Formatted post string
        """
        emoji_pnl = "📈" if pnl > 0 else "📉"
        emoji_rank = "🏆" if leaderboard_rank and leaderboard_rank <= 10 else "🎯"

        rank_text = f"\nLeaderboard: {emoji_rank} #{leaderboard_rank}" if leaderboard_rank else ""

        post = f"""{emoji_pnl} AURORA-AI Trading Update:
- Snapshot PnL: ${pnl:+.0f} ({pnl_percent:+.1f}%)
- Win Rate: {win_rate*100:.0f}% ({trade_count} trades)
- Sharpe Ratio: {sharpe_ratio:.2f}
- Validation: {validation_score:.0f}/100
- Reputation: {reputation_score:.0f}/100{rank_text}

#AITrading #ERC8004 #Kraken #Web3

@krakenfx @lablabai @Surgexyz_"""

        return post

    def generate_strategy_insight_post(self, insight: str, metric_name: str, metric_value: float) -> str:
        """Generate a longer-form strategy insight post."""
        post = f"""🧠 AURORA-AI Strategy Insight:

{insight}

Current {metric_name}: {metric_value:.2f}

The AI agent continuously learns from market conditions, optimizing:
✓ Technical signal weighting (RSI/MACD/EMA)
✓ Position sizing via confidence scores
✓ Risk management based on volatility regimes

Real-time decision reasoning posted to blockchain for transparency.

#AITrading #ERC8004 #Explainability"""

        return post

    def generate_weekly_summary_post(
        self,
        weekly_pnl: float,
        best_trade_pnl: float,
        avg_win_size: float,
        avg_loss_size: float,
        leaderboard_rank: int,
    ) -> str:
        """Generate a weekly summary post."""
        post = f"""📊 AURORA-AI Weekly Summary:

✅ Weekly PnL: ${weekly_pnl:+.0f}
✅ Best Trade: ${best_trade_pnl:+.0f}
✅ Avg Win: ${avg_win_size:.2f}
✅ Avg Loss: ${avg_loss_size:.2f}
✅ Leaderboard: #{leaderboard_rank}

🤖 Built with:
- RSI/MACD/EMA Technical Analysis
- LightGBM ML Predictions
- Confidence-Driven Position Sizing
- On-Chain Validation Posting

Competing in ERC-8004 Trustless Agent Challenge 🏆

#AITrading #Blockchain #Hackathon #Trading"""

        return post

    async def post_to_twitter(self, text: str, verbose: bool = False) -> bool:
        """
        Post to Twitter/X. Requires tweepy integration.

        Args:
            text: Post content
            verbose: Log details

        Returns:
            Success status
        """
        if not self.enable_twitter:
            if verbose:
                logger.warning("Twitter integration not enabled (missing TWITTER_BEARER_TOKEN)")
            return False

        try:
            # Integration point for tweepy v2 API
            # import tweepy
            # client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            # response = client.create_tweet(text=text)
            # logger.info(f"✅ Posted to Twitter: {response.data['id']}")

            logger.info(f"📱 [TWITTER] {text[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            return False

    async def post_to_linkedin(self, text: str, verbose: bool = False) -> bool:
        """
        Post to LinkedIn. Requires linkedin-api integration.

        Args:
            text: Post content
            verbose: Log details

        Returns:
            Success status
        """
        if not self.enable_linkedin:
            if verbose:
                logger.warning("LinkedIn integration not enabled (missing LINKEDIN_ACCESS_TOKEN)")
            return False

        try:
            # Integration point for linkedin-api
            # from linkedin_api import Linkedin
            # li = Linkedin(self.linkedin_access_token)
            # li.post(text)
            # logger.info(f"✅ Posted to LinkedIn")

            logger.info(f"💼 [LINKEDIN] {text[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            return False

    async def post_daily_update(
        self,
        metrics: Dict[str, Any],
        channels: Optional[list] = None,
    ) -> Dict[str, bool]:
        """
        Post daily metrics update to configured channels.

        Args:
            metrics: Dict with keys: pnl, pnl_percent, win_rate, trade_count,
                     sharpe_ratio, validation_score, reputation_score, leaderboard_rank
            channels: Which channels to post to (default: ['twitter', 'linkedin'])

        Returns:
            Dict with results per channel
        """
        if channels is None:
            channels = ["twitter", "linkedin"]

        post_text = self.generate_daily_update_post(
            pnl=metrics["pnl"],
            pnl_percent=metrics["pnl_percent"],
            win_rate=metrics["win_rate"],
            trade_count=metrics["trade_count"],
            sharpe_ratio=metrics["sharpe_ratio"],
            validation_score=metrics["validation_score"],
            reputation_score=metrics["reputation_score"],
            leaderboard_rank=metrics.get("leaderboard_rank"),
        )

        results = {}

        if "twitter" in channels:
            results["twitter"] = await self.post_to_twitter(post_text)

        if "linkedin" in channels:
            results["linkedin"] = await self.post_to_linkedin(post_text)

        logger.info(f"Daily update posted: {results}")
        return results

    async def post_strategy_insight(
        self,
        insight: str,
        metric_name: str,
        metric_value: float,
        channels: Optional[list] = None,
    ) -> Dict[str, bool]:
        """
        Post strategy insight to configured channels.

        Args:
            insight: Description of the insight
            metric_name: Metric being discussed
            metric_value: Current value of metric
            channels: Which channels to post to

        Returns:
            Dict with results per channel
        """
        if channels is None:
            channels = ["twitter", "linkedin"]

        post_text = self.generate_strategy_insight_post(insight, metric_name, metric_value)

        results = {}

        if "twitter" in channels:
            results["twitter"] = await self.post_to_twitter(post_text)

        if "linkedin" in channels:
            results["linkedin"] = await self.post_to_linkedin(post_text)

        logger.info(f"Strategy insight posted: {results}")
        return results

    async def post_weekly_summary(
        self,
        metrics: Dict[str, Any],
        channels: Optional[list] = None,
    ) -> Dict[str, bool]:
        """
        Post weekly summary to all channels.

        Args:
            metrics: Dict with weekly_pnl, best_trade_pnl, avg_win_size, avg_loss_size, leaderboard_rank
            channels: Which channels to post to

        Returns:
            Dict with results per channel
        """
        if channels is None:
            channels = ["twitter", "linkedin"]

        post_text = self.generate_weekly_summary_post(
            weekly_pnl=metrics["weekly_pnl"],
            best_trade_pnl=metrics["best_trade_pnl"],
            avg_win_size=metrics["avg_win_size"],
            avg_loss_size=metrics["avg_loss_size"],
            leaderboard_rank=metrics["leaderboard_rank"],
        )

        results = {}

        if "twitter" in channels:
            results["twitter"] = await self.post_to_twitter(post_text)

        if "linkedin" in channels:
            results["linkedin"] = await self.post_to_linkedin(post_text)

        logger.info(f"Weekly summary posted: {results}")
        return results


# Scheduler integration example (can be used with APScheduler)
class SocialScheduler:
    """
    Scheduler for automated social posting.
    Integrate with APScheduler or similar for production use.
    """

    def __init__(self):
        self.poster = SocialPoster()
        self.last_daily_post = None
        self.last_weekly_post = None

    async def maybe_post_daily(self, metrics: Dict[str, Any]) -> bool:
        """
        Post daily update if time has passed since last post.
        Target: 9 AM and 6 PM daily.
        """
        now = datetime.now()

        # Check if it's 9 AM or 6 PM
        if now.hour not in [9, 18]:
            return False

        # Don't post multiple times in same hour
        if self.last_daily_post and (now - self.last_daily_post).seconds < 3600:
            return False

        result = await self.poster.post_daily_update(metrics)
        self.last_daily_post = now
        return all(result.values())

    async def maybe_post_weekly(self, metrics: Dict[str, Any]) -> bool:
        """
        Post weekly summary on Sundays at 12 PM.
        """
        now = datetime.now()

        # Check if it's Sunday at noon
        if now.weekday() != 6 or now.hour != 12:
            return False

        # Don't post multiple times
        if self.last_weekly_post and (now - self.last_weekly_post).days < 7:
            return False

        result = await self.poster.post_weekly_summary(metrics)
        self.last_weekly_post = now
        return all(result.values())
