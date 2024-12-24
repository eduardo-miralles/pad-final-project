import streamlit as st
import krakenex
import matplotlib.pyplot as plt
import mplfinance as mpf

from krakenex_utils import (
    fetch_asset_pairs, 
    fetch_ohlc_data, 
    compute_bollinger_bands
)


def main():
    # Initialize Kraken API
    api = krakenex.API()

    # Streamlit App
    st.title("Kraken Pair Price Chart")

    available_pairs = fetch_asset_pairs(api)

    # User input for the trading pair
    pair = st.selectbox(
        "Enter the Kraken trading pair (XBT for Bitcoin):",
        list(available_pairs.keys()), 
        index = list(available_pairs.keys()).index("ETH/USDT")
    )
    interval = st.selectbox(
        "Select the interval (minutes):",
        [1, 5, 15, 30, 60, 240, 1440],
        index = 4
    )

    pair_kraken_name = available_pairs[pair]

    if st.button("Fetch and Plot"):
        # Fetch the data
        ohlc_df = fetch_ohlc_data(api, pair_kraken_name, interval)
        
        if ohlc_df is not None:
            # Compute Bollinger Bands
            bollinger_df = compute_bollinger_bands(ohlc_df)

            # Plotting within Streamlit
            ohlc_bollinger_df = bollinger_df.tail(180)  # tradingview shows up to 172 bars

            fig, axlist = mpf.plot(
                ohlc_bollinger_df,
                type = 'candlestick',
                style = 'tradingview',
                volume = True,
                tight_layout = True,
                addplot = [
                    mpf.make_addplot(ohlc_bollinger_df['upper_band'], type = "line", width = 1, color='royalblue'),
                    mpf.make_addplot(ohlc_bollinger_df['middle_band'], type = "line", color='orange'),
                    mpf.make_addplot(ohlc_bollinger_df['lower_band'], type = "line", width = 1, color='royalblue'),
                ],
                figsize = (12, 8),
                panel_ratios = (3, 1), 
                returnfig = True
            )

            # Rescale Y-Axis
            ymax = ohlc_bollinger_df['upper_band'].max()
            ymin = ohlc_bollinger_df['lower_band'].min()
            axlist[0].set_ylim([ymin - (ymax - ymin) / 10, ymax + (ymax - ymin) / 10])

            axlist[0].set_title(
                f"Price Chart for {pair} (Interval: {interval} minutes)", 
                fontsize = "xx-large", 
                color = "black"
            )

            # Use Streamlit to display the plot
            st.pyplot(fig)
        else:
            st.error("Failed to fetch data. Please check the trading pair or interval.")

if __name__ == "__main__":
    main()