import streamlit as st
import krakenex
import matplotlib.pyplot as plt
import mplfinance as mpf

from krakenex_utils import (
    fetch_asset_pairs, 
    fetch_ohlc_data, 
    compute_bollinger_bands, 
    downsample_ohlc_data
)


def main():
    # Initialize Kraken API
    api = krakenex.API()

    # Streamlit App
    st.title("Kraken Pair Price Chart")

    available_pairs = fetch_asset_pairs(api)

    # User input for the trading pair
    pair = st.selectbox("Enter the Kraken trading pair (e.g., XBTUSD for BTC/USD):", available_pairs.keys())
    interval = st.selectbox("Select the interval (minutes):", [1, 5, 15, 30, 60, 240, 1440])

    pair_kraken_name = available_pairs[pair]

    if st.button("Fetch and Plot"):
        # Fetch the data
        ohlc_df = fetch_ohlc_data(api, pair_kraken_name, interval)
        
        if ohlc_df is not None:
            # Compute Bollinger Bands
            window = 20  # 20-period moving average
            num_std_dev = 2  # 2 standard deviations
            bollinger_df = compute_bollinger_bands(ohlc_df, window, num_std_dev)

            # Plot the data
            st.write(f"Price Chart for {pair} (Interval: {interval} minutes)")

            # Plotting within Streamlit
            ohlc_downsample_df = downsample_ohlc_data(ohlc_df, interval)

            ohlc_downsample_bb_df = ohlc_downsample_df.merge(
                bollinger_df[["SMA", "upper_band", "lower_band"]],
                how = "left", 
                right_index = True, 
                left_index = True
            )

            ohlc_downsample_bb_df = ohlc_downsample_bb_df.loc[~ohlc_downsample_bb_df["SMA"].isnull(), :]

            fig, axlist = mpf.plot(
                ohlc_downsample_bb_df,
                type = 'candlestick',
                style = 'tradingview',
                volume = True,
                tight_layout = True,
                addplot = [
                    mpf.make_addplot(ohlc_downsample_bb_df['upper_band'], linewidths = 0.1, color='royalblue'),
                    mpf.make_addplot(ohlc_downsample_bb_df['SMA'], color='orange'),
                    mpf.make_addplot(ohlc_downsample_bb_df['lower_band'], linewidths = 0.1, color='royalblue'),
                ],
                figsize = (12, 8),
                panel_ratios = (3, 1), 
                returnfig = True
            )

            # axlist[0].set_xlim([ohlc_downsample_bb_df.index[0], ohlc_downsample_bb_df.index[-1]])
            axlist[0].set_ylim([0.999*ohlc_downsample_bb_df['lower_band'].min(), 1.001*ohlc_downsample_bb_df['upper_band'].max()])

            fig.subplots_adjust(hspace = 10) 

            # Use Streamlit to display the plot
            st.pyplot(fig)
        else:
            st.error("Failed to fetch data. Please check the trading pair or interval.")

if __name__ == "__main__":
    main()