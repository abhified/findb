"""
Custom constructs
"""
from dataclasses import dataclass


@dataclass
class FTweet:
    """
    Contains all the information for a given tweet that we need in order
    to arrive at the final sentiment.
    """

    text: str
    author_followers_count: int
    sentiment_score: int
