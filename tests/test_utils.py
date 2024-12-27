import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

from pad_final_project.utils import (
    fetch_asset_pairs,
    fetch_ohlc_data,
    compute_bollinger_bands,
    compute_rsi,
    buy_signal,
    sell_signal
)

@pytest.fixture
def mock_api():
    return MagicMock()

def test_fetch_asset_pairs(mock_api):
    mock_response = {
        "result": {
            "XXBTZUSD": {"wsname": "XBT/USD"},
            "XETHZUSD": {"wsname": "ETH/USD"}
        }, 
        "error": []
    }
    mock_api.query_public.return_value = mock_response

    expected_pairs = {"XBT/USD": "XXBTZUSD", "ETH/USD": "XETHZUSD"}
    assert fetch_asset_pairs(mock_api) == expected_pairs

def test_fetch_asset_pairs_error(mock_api):
    # Mock the API response
    mock_response = {
        "result": {}, 
        "error": ["Some error"]
    }
    mock_api.query_public.return_value = mock_response

    with pytest.raises(Exception):
        fetch_asset_pairs(mock_api)

def test_fetch_ohlc_data(mock_api):
    mock_response = {
        "result": {
            "XXBTZUSD": [
                [1616668800, "58000.0", "59000.0", "57000.0", "58000.0", "58000.0", "100.0", 100]
            ]
        },
        "error": []
    }
    mock_api.query_public.return_value = mock_response

    expected_df = pd.DataFrame(
        {
            "open": [58000.0],
            "high": [59000.0],
            "low": [57000.0],
            "close": [58000.0],
            "vwap": [58000.0],
            "volume": [100.0],
            "count": [100]
        },
        index=pd.to_datetime([1616668800], unit="s")
    )
    expected_df.index.name = "time"
    
    result_df = fetch_ohlc_data(mock_api, "XXBTZUSD")
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_fetch_ohlc_data_error(mock_api):
    # Mock API response with error
    mock_response = {
        "result": {}, 
        "error": ["Some error"]
    }
    mock_api.query_public.return_value = mock_response

    # Call the function and assert it raises an exception
    with pytest.raises(Exception):
        fetch_ohlc_data(mock_api, "INVALID_PAIR", 60)

def test_compute_bollinger_bands():
    data = {
        "close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    df = pd.DataFrame(data)
    result_df = compute_bollinger_bands(df, window=2, num_std=1)

    assert "upper_band" in result_df.columns
    assert "lower_band" in result_df.columns
    assert "middle_band" in result_df.columns

def test_compute_rsi():
    data = {
        "close": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    df = pd.DataFrame(data)
    result_series = compute_rsi(df, period=2)

    assert isinstance(result_series, pd.Series)
    assert len(result_series) == len(df)

def test_buy_signal():
    data = {
        "percent_b": [0.1, -0.1, -0.2, -0.3, -0.4],
        "low": [1, 2, 3, 4, 5],
        "RSI": [50, 40, 30, 20, 10],
        "upper_band": [6, 6, 6, 6, 6],
        "lower_band": [0, 0, 0, 0, 0]
    }
    df = pd.DataFrame(data)
    result_series = buy_signal(df)

    assert isinstance(result_series, pd.Series)
    assert len(result_series) == len(df)

def test_sell_signal():
    data = {
        "percent_b": [0.9, 1.1, 1.2, 1.3, 1.4],
        "high": [1, 2, 3, 4, 5],
        "RSI": [50, 60, 70, 80, 90],
        "upper_band": [6, 6, 6, 6, 6],
        "lower_band": [0, 0, 0, 0, 0]
    }
    df = pd.DataFrame(data)
    result_series = sell_signal(df)

    assert isinstance(result_series, pd.Series)
    assert len(result_series) == len(df)