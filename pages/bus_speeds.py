import pandas as pd
import streamlit as st
import altair as alt
    
#TASK #1: Write a Title that says 'Bus Speeds' using streamlit st.title()

#Task #2: Write a header for Bus Speeds st.header()

#TASK #3: Write description for Bus Speeds data using st.write()

# Task #4: Read MTA Bus Speeds: Beginning 2020 data upload
data_url = "https://data.ny.gov/api/views/6ksi-7cxr/rows.csv?accessType=DOWNLOAD&sorting=true"

bus_speed = pd.read_csv(data_url) #transform to pandas dataframe

# Lets look at the types of data in this
print(bus_speed.dtypes)

#Task 5: Lets look at the dataframe we just read using st.dataframe(bus_speed) #This displays the dataframe using streamlit


# Organize the Streamlit app
st.header("MTA Bus Speed Data")

st.write("This app displays the average bus speeds for different boroughs in New York City.")

# st.selectbox() creates a dropdown for the user to select one option from
borough = st.selectbox(
    label="Select a borough",
    # Let's make the options of this select box the unique values of boroughs
    options = bus_speed["borough"].unique().tolist()
)

# let's look at what type of data the date column is
print(type(bus_speed.month.iat[0]))

# Convert month column to datetime object, and lets extract the date from that object
bus_speed['month'] = pd.to_datetime(
    arg=bus_speed['month'],
    format='%Y-%m'
).dt.date

# Define date range for the filter
min_date = bus_speed['month'].min()
max_date = bus_speed['month'].max()

# Create a date range filter using streamlit
start_date, end_date = st.date_input(
    label="Select date range",
    # giving a value of a list or tuple here lets the user select a date range; if we wanted the user to select an individual date instead, only give one value
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Apply filters
# the .loc method lets us filter
df_filtered = bus_speed.loc[(bus_speed["month"] >= start_date) & (bus_speed["month"] <= end_date) & (bus_speed["borough"] == borough)]

#Task #6: Calculate average speed by month
#using groupby to find monthly average total
df_avg = df_filtered.groupby(["month"], as_index = False).agg(
        {"total_mileage": "sum", 
         "total_operating_time": "sum"}
)

df_avg["average_speed"] = df_avg["total_mileage"] / df_avg["total_operating_time"] #calculating average speed

# pull max - and add 20%
max_avg_speed = df_avg["average_speed"].max()
max_avg_speed = max_avg_speed + 0.2 * max_avg_speed

# we can use the rename method of pandas dataframes to make more descriptive columns

#Task #7: Rename columns average_speed column to "Average speed (mph)" and month to "Date"
df_avg = df_avg.rename(
    columns = {
        "average_speed" : "Average speed (mph)",
        "month" : "Date"
    }
)

# Create Altair chart
chart = alt.Chart(df_avg).mark_line().encode(
    x=alt.X('Date'), #x-axis
    y=alt.Y(
        'Average speed (mph)', 
        title='Average Bus Speed (mph)', 
        scale=alt.Scale(zero=True, domain=[0, max_avg_speed])
    ), #setting up y-axis minimum to be 0
    tooltip=[
        alt.Tooltip('Date'), 
        alt.Tooltip('Average speed (mph)', title='Average Bus Speed (mph)')
    ]
).properties(
    title=f"Average Bus Speed in {borough} from {start_date} to {end_date}"
)

# Display chart and table
st.altair_chart(chart, use_container_width=True)

