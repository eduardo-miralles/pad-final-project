import pandas as pd
import numpy as np
import krakenex


def fetch_asset_pairs(api):

    response = api.query_public('AssetPairs')
    pairs = {response['result'][key]["altname"]: key for key in response['result'].keys()}

    return pairs


def fetch_ohlc_data(api, pair, interval=60):
    """Fetch OHLC data for a given trading pair and interval."""

    params = {
        'pair': pair,
        'interval': interval
    }
    response = api.query_public('OHLC', params)
    if response['error']:
        raise Exception(f"Error: {response['error']}")
    
    ohlc_data = response['result'][pair]
    ohlc_df = pd.DataFrame(
        ohlc_data,
        columns=[
            'time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'
        ]
    )
    # Cast Unix timestamp to datetime
    ohlc_df['time'] = pd.to_datetime(ohlc_df['time'], unit='s')
    ohlc_df.set_index('time', inplace=True)  # Set 'time' as the index for plotting
    # Cast prices as floats
    price_items = ['open', 'high', 'low', 'close', 'vwap', 'volume']
    ohlc_df = ohlc_df.astype({f'{item}': 'float' for item in price_items})

    return ohlc_df


def compute_bollinger_bands(df, window=20, num_std_dev=2):
    """Compute Bollinger Bands for a given DataFrame of OHLC data."""

    # Compute the rolling mean and standard deviation
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    
    # Compute the Bollinger Bands
    df['upper_band'] = df['SMA'] + (num_std_dev * df['STD'])
    df['lower_band'] = df['SMA'] - (num_std_dev * df['STD'])
    
    return df


def downsample_ohlc_data(ohlc_df, interval):

    df_resampled = ohlc_df.resample(f'{4*interval}min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'vwap': 'mean',
        'volume': 'sum',
        'count': 'sum'
    })

    return df_resampled