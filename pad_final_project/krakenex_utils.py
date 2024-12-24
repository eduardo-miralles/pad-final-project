import pandas as pd
import numpy as np


def fetch_asset_pairs(api):

    response = api.query_public("AssetPairs")
    pairs = {response["result"][key]["wsname"]: key for key in response["result"].keys()}

    return pairs


def fetch_ohlc_data(api, pair, interval = 60):
    """Fetch OHLC data for a given trading pair and interval."""

    params = {
        "pair": pair,
        "interval": interval
    }
    response = api.query_public("OHLC", params)

    if response["error"]:
        raise Exception(f"Error: {response["error"]}")
    
    ohlc_data = response["result"][pair]
    ohlc_df = pd.DataFrame(
        ohlc_data,
        columns = [
            "time", "open", "high", "low", "close", "vwap", "volume", "count"
        ]
    )

    # Cast Unix timestamp to datetime
    ohlc_df["time"] = pd.to_datetime(ohlc_df["time"], unit = "s")
    ohlc_df.set_index("time", inplace = True)  # Set "time" as the index for plotting

    # Cast prices as floats
    price_items = ["open", "high", "low", "close", "vwap", "volume"]
    ohlc_df = ohlc_df.astype({f"{item}": "float" for item in price_items})

    return ohlc_df


def compute_bollinger_bands(df, window = 20, num_std_dev = 2):
    """Compute Bollinger Bands for a given DataFrame of OHLC data."""

    # Compute the rolling mean and standard deviation
    df["SMA"] = df["close"].rolling(window = window).mean()
    df["STD"] = df["close"].rolling(window = window).std()
    
    # Compute the Bollinger Bands
    df["upper_band"] = df["SMA"] + (num_std_dev * df["STD"])
    df["lower_band"] = df["SMA"] - (num_std_dev * df["STD"])

    # Percent B indicator
    df["percent_b"] = (df["close"] - df["lower_band"]) / (df["upper_band"] - df["lower_band"])

    # Enhance the DataFrame
    df = df.rename(columns = {"SMA": "middle_band"})
    df = df.drop(columns = ["STD"])
    
    return df


def compute_rsi(df, column="close", period=14):
    """
    Compute the Relative Strength Index (RSI) for a given DataFrame.
    
    Parameters:
    - df: DataFrame containing price data.
    - column: The column name with price data (default is "close").
    - period: The lookback period for RSI calculation (default is 14).
    
    Returns:
    - A pandas Series with RSI values.
    """
    # Calculate price changes
    delta = df[column].diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    # Calculate average gains and losses
    avg_gain = gains.ewm(span=period).mean()
    avg_loss = losses.ewm(span=period).mean()

    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def buy_signal(df):

    percentB = df["percent_b"]
    price = df["low"]
    rsi = df["RSI"]
    bollinger_diff = df["upper_band"] - df["lower_band"]

    signal = []
    index = []
    previous = -1.0

    for date, value in percentB.items():
        if value < 0 and previous >= 0 and rsi[date] <= 30:
            signal.append(price[date] - bollinger_diff[date] / 5)
        else:
            signal.append(np.nan)
        index.append(date)
        previous = value
    
    return pd.Series(signal, index)


def sell_signal(df):
    
    percentB = df["percent_b"]
    price = df["high"]
    rsi = df["RSI"]
    bollinger_diff = df["upper_band"] - df["lower_band"]

    signal = []
    index = []
    previous = -1.0

    for date, value in percentB.items():
        if value > 1 and previous <= 1 and rsi[date] >= 70:
            signal.append(price[date] + bollinger_diff[date] / 5)
        else:
            signal.append(np.nan)
        index.append(date)
        previous = value
    
    return pd.Series(signal, index)