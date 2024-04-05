# Imports at the top - PyShiny EXPRESS VERSION
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg
import requests

# First, set a constant UPDATE INTERVAL for all live data
UPDATE_INTERVAL_SECS: int = 3

# Initialize a REACTIVE VALUE with a common data structure
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))
√
# Function to fetch recent data based on location zip code
def fetch_recent_data(zip_code):
    # Make a request to fetch recent data based on the zip code
    # Replace the URL with your actual data source
    response = requests.get(f"https://api.example.com/recent_data?zip_code={zip_code}")
    
    # Parse the response and return relevant data
    if response.status_code == 200:
        data = response.json()
        return data.get("temperature"), data.get("timestamp")
    else:
        return None, None

# Initialize a REACTIVE CALC that all display components can call
@reactive.calc()
def reactive_calc_combined(zip_code: str):
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Get recent data based on location zip code
    temperature, timestamp = fetch_recent_data(zip_code)
    
    # Return temperature and timestamp
    return temperature, timestamp

# Define the Shiny UI Page layout
ui.page_opts(title="PyShiny Express: Live Data Example", fillable=True)

# Sidebar for user interaction/information
with ui.sidebar(open="open"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/jg2012/cintel-05-cintel/tree/main",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://github.com/jg2012/cintel-05-cintel/blob/main/dashboard/app.py",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a(
        "PyShiny Express",
        href="hhttps://shiny.posit.co/blog/posts/shiny-express/",
        target="_blank",
    )
    # Input field for location zip code
    zip_code_input = ui.text_input(label="Enter location zip code", placeholder="Enter zip code here", value="")

# Main panel layout
with ui.layout_columns():
    # Display current temperature
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-blue-purple",
    ):
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            temperature, _ = reactive_calc_combined(zip_code_input.value)
            return f"{temperature} C" if temperature is not None else "N/A"

    # Display current date and time
    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")
        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            _, timestamp = reactive_calc_combined(zip_code_input.value)
            return f"{timestamp}" if timestamp is not None else "N/A"

    # Display most recent readings in a dataframe
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            temperature, timestamp = reactive_calc_combined(zip_code_input.value)
            if temperature is not None and timestamp is not None:
                df = pd.DataFrame({"Temperature (C)": [temperature], "Timestamp": [timestamp]})
                pd.set_option('display.width', None)
                return render.DataGrid(df, width="100%")
            else:
                return "No data available"

    # Display chart with current trend
    with ui.card():
        ui.card_header("Chart with Current Trend")
        @render_plotly
        def display_plot():
            temperature, timestamp = reactive_calc_combined(zip_code_input.value)
            if temperature is not None and timestamp is not None:
                # Create a dummy dataframe with current temperature and timestamp
                df = pd.DataFrame({"timestamp": [timestamp], "temp": [temperature]})
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Create scatter plot with regression line
                fig = px.scatter(df,
                                 x="timestamp",
                                 y="temp",
                                 title="Temperature Readings with Regression Line",
                                 labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                                 color_discrete_sequence=["blue"])

                # Add linear regression line
                sequence = range(len(df))
                x_vals = list(sequence)
                y_vals = df["temp"]
                slope, intercept, _, _, _ = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')
                fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
                return fig
            else:
                return "No data available"
