import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.header("Bus Customer Journey Time Performance")

# read in data 
busjourney = pd.read_csv("https://data.ny.gov/api/views/wrt8-4b59/rows.csv?accessType=DOWNLOAD&sorting=true")

# task 1: lets look at the dataset we just read in with the st.dataframe function

st.write(
    "This page lets the user interact with customer journey focused metric data to produce their own visualizations and data tables. Each row in the bus customer journey focused metric dataset reflects a bus route, on a type of route, at a time of day, aggregated over a month"
)

st.markdown("- *Additional Bus Stop Time* is the average time that customers spend waiting at a stop beyond their scheduled wait time")

st.markdown("- *Additional Travel Time* is the average time customers spend onboard a bus beyond their scheduled travel time")

st.markdown("- *Customer Journey Time Performance* is the percentage of customers whose journeys are completed within 5 minutes of the scheduled time.")

st.markdown("**You can use `st.markdown`** to *style* text how you want")

# lets set the month column as datetime so it works with our filters
busjourney.month = pd.to_datetime(busjourney.month, format='%Y-%m').dt.date

# let's try to make a line chart comparing different routes, and a bar chart, based on different filters, and then to show the data at the end
# lets start with a date filter
maxmonth = busjourney.month.max()
minmonth = busjourney.month.min()

select_date = st.date_input(
    "Enter a start and end date",
    # supplying two dates means that in streamlit, we'll be able to pick a start and end date
    value=[minmonth, maxmonth],
    min_value=minmonth,
    max_value=maxmonth
)


# task 2: print the values stored by selectdate


# let's now filter the data to the selected dates - st.dateinput returns a list of length 2 with the start and end date
busjourney = busjourney.loc[
    (busjourney["month"] >= select_date[0]) & (busjourney['month'] <= select_date[1])
]

# now - lets add a select filter for trip type
# note: we could just write out the trip types, but it's better practice to pull directly from the dataset in case the underlying data changes (e.g., there's a new trip type 'Misc', or 'Slightly faster than Local but less fast than Express')
# the `unique()` method pulls unique values from a series; the `tolist()` method converts it to a list type  
trip_opts = busjourney.trip_type.unique().tolist()

# let's make sure the options are sorted by using the `sort` method of lists - these modify the object in place, so we don't need to set trip_opts equal to this (and doing so actually breaks things, because the sort method returns None)
trip_opts.sort()

select_trips = st.selectbox(
    label="Select which trip-types to include",
    options=trip_opts,
    # lets make the first option selected by default
    index=0
)

# lets only compare routes that have the same trip type
busjourney = busjourney.loc[busjourney["trip_type"] == select_trips]

# lets now pull the unique period options
period_opts = busjourney["period"].unique().tolist()

# let's now make a radio button of whether we want peak period or not
select_period = st.radio(
    label="Select a period",
    options=period_opts,
    # lets start with the second option
    index=1
)

# lets now filter the dataset to the selected period with the loc method- so other options we pull will reflect our filter
busjourney = busjourney.loc[busjourney['period'] == select_period]

# now let's add a borough filter. but what if the user wants to compare routes in multiple boroughs? let's use a multiselect
boro_opts = busjourney.borough.unique().tolist()

boro_opts.sort()

select_boro = st.multiselect(
    label="Select which boroughs to include",
    options=boro_opts,
    # lets make the first borough displayed
    default=boro_opts[0]
)

# now - let's shrink the dataset tp reflect the selected boroughs
# the isin method to series checks if each value in the series is in the list of values supplied to the isin method
busjourney = busjourney.loc[busjourney["borough"].isin(select_boro)]

route_opts = busjourney.route_id.unique().tolist()

route_opts.sort()

# finally - lets make a multiselect filter for route
select_routes = st.multiselect(
    label="Select which routes to include",
    options=route_opts,
    # lets make 2 routes display
    default=route_opts[0:2]
)

# and lets filter the bus data to the routes
busjourney = busjourney.loc[busjourney["route_id"].isin(select_routes)]

# we're going to make some charts later - let's pick which metric we want visualized in the chart
# accessing the columns attribute of the busjourney dataframe
metric_opts = busjourney.columns

# task 3: let's look at the columns here, and then modify metric_opts to only include the columns we want the user to be able to visualize

# this selects numeric columns
metric_opts = busjourney.select_dtypes([np.number]).columns

select_metric = st.selectbox(
    "Select which metric you want to visualize",
    metric_opts
)

# lets add a slider filter based on the maximum and minimum values of the selected metric
min_slider = busjourney[select_metric].min()
max_slider = busjourney[select_metric].max()

select_slider = st.slider(
    'Filter the data to the range of the selected metric',
    value=[min_slider, max_slider],
    min_value=min_slider,
    max_value=max_slider
)

busjourney = busjourney.loc[(busjourney[select_metric] >= select_slider[0]) & (busjourney[select_metric] <= select_slider[1])]

select_bar_title = st.text_input(
    label="Write a title for the bar chart",
    value = "Number of customers by borough"
)


# task 4: these are a lot of selectors. lets organize these selectors in columns with `st.columns` and `st.expander`

# task 5: this is a lot of information straight down. lets organize these charts and the dataframe with `st.tabs()`

# let's look at the output dataset
st.dataframe(busjourney, use_container_width=True)

# let's initialize a chart of this data with altair
basechart = alt.Chart(busjourney)

# lets use the mark_line method to turn this into a line chart, and then the encode method to set our x and y axis
bus_lines = (
    basechart.mark_line().encode(
        x = 'month',
        y = select_metric,
    )
    .properties(title = f"{select_metric} by month")
    .interactive()
)

# task 6: something looks off about this - what's the problem? and what should we do to fix it
st.altair_chart(bus_lines, use_container_width=True)

# and lastly, let's create a bar chart this time - comparing selected boroughs
bus_bar = (
    basechart.mark_bar().encode(
        # alt.x and alt.y let you specify options more directly
        x = alt.X(field = 'borough'),
        y = alt.Y(field = select_metric, type='quantitative'),
        # we can use the tooltip parameter to make a tooltip
        tooltip=[
            alt.Tooltip('borough'), 
            alt.Tooltip(select_metric, type='quantitative')
        ]
    )
    .properties(title = select_bar_title)
    .interactive()
)

# task 7: something also looks off about this chart - what's wrong with it? And what do we want to do to fix it
st.altair_chart(bus_bar, use_container_width=True)


# task 8: it gets a little cluttered looking at all of this together - reorganize the line chart, bar chart, and dataframe so it's more legible

# bonus task: if only one borough is selected, the bar chart isn't that useful. hide the bar chart and tab if only one borough is selected with an `if` statement

# lets let the user download the data they've filtered
st.download_button("Download data", 
                   data=busjourney.to_csv(encoding = 'utf-8'), file_name="busjourney.csv")
