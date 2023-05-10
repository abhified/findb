"""
Root file for the twitter utils
"""
from datetime import datetime, timedelta

import tweepy
from pytz import timezone

from twitter_utils.auth_utils import get_access_token
from twitter_utils.nlp_utils import generate_ftweets, get_overall_sentiment_from_ftweets


def get_sentiment(symbol: str) -> float:
    """
    Fetches the sentiment for the preceding 2 days given a symbol name
    """
    # Fetch the access token through the OAuth-2.0 flow
    access_token = get_access_token()

    # Spawn a Tweepy client to then search for tweets
    twc = tweepy.Client(bearer_token=access_token)

    try:
        limit = 0

        tweets: list[tweepy.Tweet] = []
        users: list[tweepy.User] = []
        next_token = None

        while limit < 10:
            api_response = twc.search_recent_tweets(
                query=f"#{symbol} -is:retweet",
                # Start the query from 2 days ago
                start_time=(
                    (datetime.now() - timedelta(days=2))
                    .astimezone(tz=timezone("UTC"))
                    .strftime("%Y-%m-%dT%H:%M:%SZ")
                ),
                # End the query at the current time
                end_time=(
                    # End time must be at least 10 seconds prior to the request time.
                    # Just offset by a minute to be safe.
                    (datetime.now() - timedelta(minutes=1))
                    .astimezone(tz=timezone("UTC"))
                    .strftime("%Y-%m-%dT%H:%M:%SZ")
                ),
                max_results=100,
                # Add arguments to fetch the user details to help weight results
                # according to their follower count.
                expansions=["author_id"],
                user_fields=["public_metrics"],
                # Attach the next_token for pagination.
                next_token=next_token,
            )
            tweets.extend(api_response.data)
            users.extend(api_response.includes["users"])

            try:
                next_token = api_response.meta["next_token"]
            except KeyError:
                break

            limit += 1
    except tweepy.TweepyException as _e:
        print(f"Error fetching tweets: {_e}")
        return

    print("got tweets")

    sorted_tweets = sorted(
        tweets,
        reverse=True,
        key=lambda t: next(
            (user for user in users if user.id == t.author_id), None
        ).public_metrics["followers_count"],
    )

    ftweets = generate_ftweets(
        tweets=sorted_tweets[
            : 50 if len(sorted_tweets) > 50 else len(sorted_tweets) - 1
        ],
        user_details=users,
    )

    return get_overall_sentiment_from_ftweets(ftweets=ftweets)
