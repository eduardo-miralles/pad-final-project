import pandas as pd
import numpy as np


# Dictionary that maps human-readable intervals to the corresponding Kraken API values
available_intervals = {
    "1 minute": 1,
    "5 minutes": 5,
    "15 minutes": 15,
    "30 minutes": 30,
    "1 hour": 60,
    "4 hours": 240,
    "1 day": 1440,
    "1 week": 10080
}


def fetch_asset_pairs(api) -> dict:
    """
    Fetch every asset pair available in Kraken.

    Args:
        api (krakenex.api.API)

    Returns:
        dict: Dictionary containing classic asset pairs names as keys and Kraken names as values
    """

    response = api.query_public("AssetPairs")
    if response["error"]:
        raise Exception(f"Error: {response["error"]}")
    
    pairs = {response["result"][key]["wsname"]: key for key in response["result"].keys()}

    return pairs


def fetch_ohlc_data(api, pair, interval = 60) -> pd.DataFrame:
    """
    Fetch OHLC data for a given trading pair and interval.

    Args:
        api (krakenex.api.API)
        pair (str): String containing the Kraken name of an asset pair
        interval (int): Time duration of each interval in minutes (default is 60)

    Returns:
        pd.DataFrame: DataFrame containing the requested OHLC data
    """

    # API call
    params = {
        "pair": pair,
        "interval": interval
    }
    response = api.query_public("OHLC", params)

    if response["error"]:
        raise Exception(f"Error: {response["error"]}")
    
    # Transform into DataFrame
    ohlc_data = response["result"][pair]
    ohlc_df = pd.DataFrame(
        ohlc_data,
        columns = [
            "time", "open", "high", "low", "close", "vwap", "volume", "count"
        ]
    )

    # Cast Unix timestamp to datetime and set as index
    ohlc_df["time"] = pd.to_datetime(ohlc_df["time"], unit = "s")
    ohlc_df.set_index("time", inplace = True)

    # Cast prices as floats
    price_items = ["open", "high", "low", "close", "vwap", "volume"]
    ohlc_df = ohlc_df.astype({f"{item}": "float" for item in price_items})

    return ohlc_df


def compute_bollinger_bands(df, column = "close", window = 20, num_std = 2) -> pd.DataFrame:
    """
    Compute Bollinger Bands for a given DataFrame of OHLC data.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data
        column (str): The column name with price data (default is "close")
        window (int): Size of the interval window for the rolling mean (default is 20)
        num_std (int): Number of standard deviatinons used to compute the Bollinger bands (default is 2)

    Returns:
        pd.DataFrame: DataFrame containing the OHLC data and Bollinger bands
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    # Compute the rolling mean and standard deviation
    df["SMA"] = df[column].rolling(window = window, min_periods = 1).mean()
    df["STD"] = df[column].rolling(window = window, min_periods = 1).std()
    
    # Compute the Bollinger Bands
    df["upper_band"] = df["SMA"] + (num_std * df["STD"])
    df["lower_band"] = df["SMA"] - (num_std * df["STD"])

    # Percent B indicator
    df["percent_b"] = (df[column] - df["lower_band"]) / (df["upper_band"] - df["lower_band"])

    # Enhance the DataFrame
    df = df.rename(columns = {"SMA": "middle_band"})
    df = df.drop(columns = ["STD"])
    
    return df


def compute_rsi(df, column = "close", period = 14) -> pd.Series:
    """
    Compute the Relative Strength Index (RSI) for a given OHLC DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing price data
        column (str): The column name with price data (default is "close")
        period (int): The lookback period for RSI calculation (default is 14)
    
    Returns:
        pd.Series: Series with RSI values
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    # Calculate price changes
    delta = df[column].diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    # Calculate average gains and losses
    avg_gain = gains.ewm(span = period).mean()
    avg_loss = losses.ewm(span = period).mean()

    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def compute_buy_signals(df) -> pd.Series:
    """
    Computes when to generate a buy signal using %B and RSI indicators.

    Args:
        df (pd.DataFrame): DataFrame containing OHLC data + Bollinger bands + %B and RSI indicators
    
    Returns:
        pd.Series: Series containing the buy signals
    """

    try:
        # Extract relevant Series from original DataFrame
        percentB = df["percent_b"]
        rsindex = df["RSI"]

        # Adjust singal sepparation for signal plots
        separation = (df["upper_band"].max() - df["lower_band"].min()) / 20

        signal = []
        index = []
        previous_pb = 0.5
        previous_rsi = 50

        for date, pb in percentB.items():
            rsi = rsindex[date]
            # Condition for buying
            buy_condition = (
                (previous_pb < 0 and pb > 0 and previous_rsi <= 30 and rsi >= previous_rsi) or
                (previous_pb < 0 and pb > previous_pb and previous_rsi <= 30 and rsi >= 30)
            )
            if buy_condition:
                signal.append(df["low"].loc[date] - separation)
            else:
                signal.append(np.nan)
            index.append(date)
            previous_pb = pb
            previous_rsi = rsi
        
        buy_signals = pd.Series(signal, index)

    except Exception as e:
        print("The input DataFrame does not contain the necessary columns. Not computing buy signals.")
        buy_signals = pd.Series([np.nan] * len(df), index=df.index)
        
    return buy_signals


def compute_sell_signals(df) -> pd.Series:
    """
    Computes when to generate a sell signal using %B and RSI indicators.

    Args:
        df (pd.DataFrame): DataFrame containing OHLC data + Bollinger bands + %B and RSI indicators
    
    Returns:
        pd.Series: Series containing the sell signals
    """
    
    try:
        # Extract relevant Series from original DataFrame
        percentB = df["percent_b"]
        rsindex = df["RSI"]

        # Adjust singal sepparation for signal plots
        separation = (df["upper_band"].max() - df["lower_band"].min()) / 20

        signal = []
        index = []
        previous_pb = 0.5
        previous_rsi = 50

        for date, pb in percentB.items():
            rsi = rsindex[date]
            # Condition for selling
            sell_condition = (
                (previous_pb > 1 and pb < 1 and previous_rsi >= 70 and rsi <= previous_rsi) or
                (previous_pb > 1 and pb < previous_pb and previous_rsi >= 70 and rsi <= 70)
            )
            if sell_condition:
                signal.append(df["high"].loc[date] + separation)
            else:
                signal.append(np.nan)
            index.append(date)
            previous_pb = pb
            previous_rsi = rsi
        
        sell_signals = pd.Series(signal, index)
        
    except Exception as e:
        print("The input DataFrame does not contain the necessary columns. Not computing sell signals.")
        sell_signals = pd.Series([np.nan] * len(df), index=df.index)
        
    return sell_signals