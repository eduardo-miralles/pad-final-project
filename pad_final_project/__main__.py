import streamlit as st
import krakenex
import mplfinance as mpf

from krakenex_utils import (
    fetch_asset_pairs, 
    fetch_ohlc_data, 
    compute_bollinger_bands, 
    compute_rsi, 
    buy_signal, 
    sell_signal
)


def main():
    # Initialize Kraken API
    api = krakenex.API()

    # Streamlit App
    st.title("Kraken Pair Price Chart")

    available_pairs = fetch_asset_pairs(api)
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

    # User input for the trading pair
    pair = st.selectbox(
        "Enter the Kraken trading pair (XBT for Bitcoin):",
        list(available_pairs.keys()), 
        index = list(available_pairs.keys()).index("ETH/USDT")
    )
    interval = st.selectbox(
        "Select the interval:",
        list(available_intervals.keys()),
        index = 4
    )

    pair_kraken_name = available_pairs[pair]
    interval_in_minutes = available_intervals[interval]

    if st.button("Fetch and Plot"):
        # Fetch the data
        ohlc_df = fetch_ohlc_data(api, pair_kraken_name, interval_in_minutes)
        
        if ohlc_df is not None:
            # Compute Bollinger Bands
            bollinger_df = compute_bollinger_bands(ohlc_df)

            # Compute RSI
            bollinger_df["RSI"] = compute_rsi(ohlc_df)

            # Plotting within Streamlit
            ohlc_bollinger_df = bollinger_df.tail(110)  # tradingview shows up to 172 bars

            buy_signals = buy_signal(ohlc_bollinger_df)
            sell_signals = sell_signal(ohlc_bollinger_df)

            apds = [
                mpf.make_addplot(
                    ohlc_bollinger_df["upper_band"],
                    type = "line",
                    width = 1,
                    color = "#EF5350"
                ),
                mpf.make_addplot(
                    ohlc_bollinger_df["middle_band"],
                    type = "line",
                    width = 1,
                    color = "RoyalBlue"
                ),
                mpf.make_addplot(
                    ohlc_bollinger_df["lower_band"],
                    type = "line",
                    width = 1,
                    color = "#28A79B"
                ), 
                mpf.make_addplot(
                    ohlc_bollinger_df["percent_b"],
                    type = "line",
                    width = 1,
                    color = "firebrick", 
                    panel = 2
                ), 
                mpf.make_addplot(
                    ohlc_bollinger_df["RSI"],
                    type = "line",
                    width = 1,
                    color = "slateblue", 
                    panel = 2
                ), 
            ]

            if not buy_signals.dropna().empty:
                apds.append(
                    mpf.make_addplot(
                        buy_signals,
                        type = "scatter",
                        markersize = 50,
                        marker = "^", 
                        label = "buy signals"
                    )
                )
            
            if not sell_signals.dropna().empty:
                apds.append(
                    mpf.make_addplot(
                        sell_signals,
                        type = "scatter",
                        markersize = 50,
                        marker = "v", 
                        label = "sell signals"
                    )
                )

            fig, axlist = mpf.plot(
                ohlc_bollinger_df,
                type = "candlestick",
                style = "tradingview",
                volume = True,
                tight_layout = True,
                addplot = apds,
                figsize = (12, 8),
                panel_ratios = (5, 1, 2), 
                returnfig = True
            )

            # Rescale Y-Axis
            ymax = max([ohlc_bollinger_df["upper_band"].max(), sell_signals.max()])
            ymin = min([ohlc_bollinger_df["lower_band"].min(), buy_signals.min()])
            axlist[0].set_ylim([ymin - (ymax - ymin) / 10, ymax + (ymax - ymin) / 10])

            axlist[4].set_ylabel("%B").set_color("firebrick")
            axlist[4].set_ylim([-0.5, 1.5])

            axlist[5].set_ylabel("RSI").set_color("slateblue")
            axlist[5].set_ylim([10, 90])
            axlist[5].set_yticks([10, 30, 50, 70, 90])

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