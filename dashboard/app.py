# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render

# From shiny.express, import just ui and inputs if needed
from shiny.express import ui

import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# --------------------------------------------
# Shiny EXPRESS VERSION
# --------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 3

# --------------------------------------------
# Initialize a REACTIVE VALUE with a common data structure
# The reactive value is used to store state (information)
# Used by all the display components that show this live data.
# This reactive value is a wrapper around a DEQUE of readings
# --------------------------------------------

DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC that all display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns a tuple with everything needed to display the data.
# Very easy to expand or modify.
# --------------------------------------------


@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic for Omaha, NE
    temp_celsius = round(random.uniform(0, 5), 1)  # Temperature range for Omaha in Celsius
    temp_fahrenheit = temp_celsius * 9/5 + 32  # Convert temperature to Fahrenheit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp": temp_fahrenheit, "timestamp": timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry


# Define the Shiny UI Page layout
# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI
ui.page_opts(title="Jose Guzman's: Live Data Example", fillable=True)

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently
with ui.sidebar(open="open"):

    ui.h2("Omaha Weather Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Omaha, NE.",
        class_="text-center",
    )
    ui.hr()
    ui.h6("Links:")
    ui.a(
        "GitHub Source",
        href="https://github.com/jg2012/cintel-05-cintel",
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

# In Shiny Express, everything not in the sidebar is in the main panel

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("cloud"),
        theme="bg-gradient-blue-orange",
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} F"

        "Is it raining, is it snowing? Is a hurricane a-blowing? - Willy Wonka" 

  

    with ui.card(full_screen=True, style="background-color: lightgray"):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
           """Get the latest reading and return a timestamp string"""
           deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
           timestamp = latest_dictionary_entry['timestamp']
           date_string = timestamp.split()[0]  # Extracting date
           time_string = timestamp.split()[1]  # Extracting time
           return f"Date: {date_string}\nTime: {time_string}"


#with ui.card(full_screen=True, min_height="40%"):
with ui.card(full_screen=True , style="background-color: lightgray"):
    ui.card_header("Most Recent Readings")

    @render.data_frame
    def display_df():
        """Get the latest reading and return a dataframe with current readings"""
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
        pd.set_option('display.width', None)        # Use maximum width
        return render.DataGrid( df,width="100%")

with ui.card(style="background-color: lightgray"):
    ui.card_header("Chart with Current Trend")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Create scatter plot for readings
            fig = px.scatter(df,
                             x="timestamp",
                             y="temp",
                             title="Temperature Readings with Regression Line",
                             labels={"temp": "Temperature (°F)", "timestamp": "Time"},
                             color_discrete_sequence=["black"])

            # Linear regression
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            # Label the regression line with its formula
            annotation_text = f'y = {slope:.2f}x + {intercept:.2f}'
            fig.add_annotation(x=df["timestamp"].iloc[int(len(df) / 2)],  # Position the annotation at the midpoint of the x-axis
                               y=df['best_fit_line'].iloc[int(len(df) / 2)],  # Position the annotation at the midpoint of the regression line
                               text=annotation_text,
                               showarrow=False,
                               font=dict(size=12, color="blue"),  # Set font properties
                               align="center",  # Center align the annotation text
                               bgcolor="lightblue",  # Set background color of the annotation
                               bordercolor="blue",  # Set border color of the annotation
                               borderwidth=1,  # Set border width of the annotation
                               borderpad=4  # Set padding of the border
                               )

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°F)")

            return fig

        # If DataFrame is empty, return an empty figure.
        else:
            return px.scatter(title="No Data Available")
