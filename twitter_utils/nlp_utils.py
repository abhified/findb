"""
Natural language processing utils
"""


import tweepy
from langdetect import detect
from scipy.special import softmax
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

from constructs import FTweet

# The pretrained model used for classification of English and Hindi tweets
_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
config = AutoConfig.from_pretrained(_MODEL)
tokenizer = AutoTokenizer.from_pretrained(_MODEL)

# PT
model = AutoModelForSequenceClassification.from_pretrained(_MODEL)

LABELS = ["Negative", "Neutral", "Positive"]


def generate_ftweets(
    tweets: list[tweepy.Tweet], user_details: list[tweepy.User]
) -> list[FTweet]:
    """
    - Replaces `@ (mentions)` and `http links` with
      generic placeholders `@user` and `http` respectively.
    - Determines language and filters out tweets that are not in English
      or Hindi since the model can't really understand others.

    Returns the list of tweets after the above transformations.
    """
    ftweet_list = []

    for tweet in tweets:
        # Clean and transform tweet
        # -------------------------
        tweet_words = []
        for word in tweet.text.split(" "):
            if detect(tweet.text) not in ["en", "hi"]:
                continue

            if word.startswith("@") and len(word) > 1:
                word = "@user"
            elif word.startswith("http"):
                word = "http"

            tweet_words.append(word)

        # Store in a convenience variable
        transformed_tweet_text = " ".join(tweet_words)

        # Determine text tweet's sentiment
        # --------------------------------
        encoded_tweet = tokenizer(transformed_tweet_text, return_tensors="pt")
        output = model(**encoded_tweet)
        scores = output[0][0].detach().numpy()

        # Convert to probability - Scores are in the order of
        # - [Negative, Neutral, Positive]
        scores = softmax(scores)
        sentiment_score = None
        if scores[0] < scores[1] and scores[2] < scores[1]:  # Neutral is highest
            sentiment_score = 0
        elif scores[0] > scores[2]:  # Negative is highest
            sentiment_score = -1 * scores[0]
        else:  # Postitive is highest
            sentiment_score = scores[2]

        # Get the tweet author's follower count
        # -------------------------------------
        user_obj = next(
            (user for user in user_details if user.id == tweet.author_id), None
        )
        if user_obj is None:
            # pylint: disable=broad-exception-raised
            raise Exception(
                f"User not found for tweet: {tweet.text}"
                f" with author_id: {tweet.author_id}."
            )

        # Store the followers_count in a convenience variable
        followers_count = user_obj.public_metrics["followers_count"]

        ftweet_list.append(
            FTweet(
                text=transformed_tweet_text,
                author_followers_count=followers_count,
                sentiment_score=sentiment_score,
            )
        )

    # Returned the populated tweet list
    return ftweet_list


def get_overall_sentiment_from_ftweets(ftweets: list[FTweet]):
    """
    Returns weighted sentiment
    """
    total_follower_count = 0
    weighted_sentiment_total = 0

    for tweet in ftweets:
        print(tweet.author_followers_count)
        weighted_sentiment_total += tweet.author_followers_count * tweet.sentiment_score
        total_follower_count += tweet.author_followers_count

    return weighted_sentiment_total / total_follower_count
