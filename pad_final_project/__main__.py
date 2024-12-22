import streamlit as st
import krakenex
import matplotlib.pyplot as plt

from krakenex_utils import (
    fetch_ohlc_data, 
    compute_bollinger_bands
)


def main():
    # Initialize Kraken API
    api = krakenex.API()

    # Streamlit App
    st.title("Kraken Pair Price Chart")

    # User input for the trading pair
    pair = st.text_input("Enter the Kraken trading pair (e.g., XXBTZUSD for BTC/USD):", value="XXBTZUSD")
    interval = st.selectbox("Select the interval (minutes):", [1, 5, 15, 30, 60, 240, 1440, 21600])

    if st.button("Fetch and Plot"):
        # Fetch the data
        ohlc_df = fetch_ohlc_data(api, pair, interval)

        # Compute Bollinger Bands
        window = 20  # 20-period moving average
        num_std_dev = 2  # 2 standard deviations
        bollinger_df = compute_bollinger_bands(ohlc_df, window, num_std_dev)
        
        if ohlc_df is not None:
            # Plot the data
            st.write(f"Price Chart for {pair} (Interval: {interval} minutes)")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(ohlc_df['time'], ohlc_df['close'], label='Close Price', color='blue')
            ax.plot(bollinger_df['time'], bollinger_df['Upper Band'], label='Upper Band', color='red')
            ax.plot(bollinger_df['time'], bollinger_df['Lower Band'], label='Lower Band', color='red')
            ax.plot(bollinger_df['time'], bollinger_df['SMA'], label='Middle Band', color='red')
            ax.set_xlabel('Time')
            ax.set_ylabel('Price')
            ax.set_title(f'{pair} Price vs Time')
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("Failed to fetch data. Please check the trading pair or interval.")

if __name__ == "__main__":
    main()