"""
FinDB task backend
"""
from json import dumps

from twitter_utils import get_sentiment


def lift_off(event: dict, _: dict) -> dict:
    """
    Start processing
    """
    try:
        try:
            symbol = str(event["queryStringParameters"]["symbol"]).upper().strip()

            if symbol not in [
                "INFY",
                "TCS",
                "HDFCBANK",
                "RELIANCE",
                "ADANIENT",
                "AXISBANK",
                "TATAMOTORS",
                "BAJFINANCE",
                "VEDANTA",
                "ASTRAL",
            ]:
                return {
                    "statusCode": 400,
                    "body": dumps({"error": "Symbol not supported"}),
                }

        # pylint: disable=broad-except
        except KeyError:
            return {
                "statusCode": 400,
                "body": dumps(
                    {"error": "Symbol not specified. Specifying symbol is mandatory."}
                ),
            }

        sentiment = get_sentiment(symbol=symbol)

        return {
            "statusCode": 200,
            "body": dumps({"symbol": symbol, "sentiment": round(sentiment * 100, 2)}),
        }
    # pylint: disable=broad-except
    except Exception as _e:
        print(_e)
        return {"statusCode": 500, "body": dumps({"error": "Internal server error"})}


if __name__ == "__main__":
    print("calling lift_off")
    print(
        lift_off(
            _={},
            event={
                "queryStringParameters": {
                    "symbol": "HDFCBANK",
                }
            },
        )
    )
