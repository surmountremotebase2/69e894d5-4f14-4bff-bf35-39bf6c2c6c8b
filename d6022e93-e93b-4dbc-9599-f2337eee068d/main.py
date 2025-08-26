from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA
from surmount.data import InstitutionalOwnership, InsiderTrading, SocialSentiment, Asset
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]
        self.data_list = [
            SocialSentiment("AAPL"),
            InstitutionalOwnership("AAPL"),
            InsiderTrading("AAPL")
        ]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        
        # Basic strategy based on social sentiment, insider trading, and RSI
        sentiment_positive = data[("social_sentiment", "AAPL")][-1]['twitterSentiment'] > 0.5
        recent_insider_sale = any(trade['transactionType'] == 'S-Sale' for trade in data[("insider_trading", "AAPL")])
        rsi_indicator = RSI("AAPL", data["ohlcv"], 14)
        
        # Ensure we have an RSI value before proceeding
        if rsi_indicator is not None:
            current_rsi = rsi_indicator[-1]
        else:
            current_rsi = None

        # Conditions to determine allocation
        if sentiment_positive and not recent_insider_sale and current_rsi is not None and current_rsi < 30:
            # Bullish scenario: social sentiment is positive, no recent insider sales, and RSI indicates oversold
            allocation_dict["AAPL"] = 1.0  # Full allocation
        elif current_rsi is not None and current_rsi > 70:
            # Bearish scenario: RSI indicates overbought
            allocation_dict["AAPL"] = 0.0  # No allocation
        else:
            # Neutral scenario: equally weighted among available assets
            allocation_dict["AAPL"] = 0.5

        return TargetAllocation(allocation_dict)