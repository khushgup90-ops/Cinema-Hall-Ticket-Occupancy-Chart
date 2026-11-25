import streamlit as st
import pandas as pd

from database import (
    initialize_database,
    get_shows,
    add_show,
    update_booked_seats,
)
from charts import (
    prepare_dataframe,
    movie_occupancy_chart,
    booked_available_chart,
)

st.set_page_config(
    page_title="Cinema Occupancy Dashboard",
    page_icon="🎬",
    layout="wide"
)

# A little CSS for a cleaner dashboard look.
st.markdown("""
<style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2rem;}
    [data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 16px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

initialize_database()

st.title("🎬 Cinema Hall Ticket Occupancy")
st.caption("Track movie shows, booked tickets, available seats and occupancy.")

# Sidebar filters
all_df = prepare_dataframe(get_shows())

with st.sidebar:
    st.header("🔎 Filters")
    movie_options = ["All Movies"] + sorted(all_df["movie_name"].unique().tolist())
    selected_movie = st.selectbox("Select movie", movie_options)

    time_options = ["All Show Times"] + sorted(all_df["show_time"].unique().tolist())
    selected_time = st.selectbox("Select show time", time_options)

    st.divider()
    st.subheader("➕ Add a Movie Show")

    with st.form("add_show_form", clear_on_submit=True):
        new_movie = st.text_input("Movie name")
        new_time = st.selectbox(
            "Show time",
            ["09:00 AM", "10:00 AM", "11:00 AM", "01:00 PM",
             "02:00 PM", "03:00 PM", "06:00 PM", "09:00 PM"]
        )
        new_total = st.number_input("Total seats", min_value=1, max_value=2000, value=150)
        new_booked = st.number_input(
            "Already booked seats", min_value=0, max_value=int(new_total), value=0
        )
        submitted = st.form_submit_button("Add show", use_container_width=True)

        if submitted:
            try:
                add_show(new_movie, new_time, int(new_total), int(new_booked))
                st.success("Show added successfully.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))

# Apply filters
df = all_df.copy()
if selected_movie != "All Movies":
    df = df[df["movie_name"] == selected_movie]
if selected_time != "All Show Times":
    df = df[df["show_time"] == selected_time]

if df.empty:
    st.warning("No shows match these filters.")
    st.stop()

# Summary metrics
total_seats = int(df["total_seats"].sum())
booked_seats = int(df["booked_seats"].sum())
available_seats = int(df["available_seats"].sum())
occupancy = (booked_seats / total_seats * 100) if total_seats else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Seats", f"{total_seats:,}")
col2.metric("Booked Tickets", f"{booked_seats:,}")
col3.metric("Available Seats", f"{available_seats:,}")
col4.metric("Occupancy", f"{occupancy:.1f}%")

st.divider()

# Charts
left_chart, right_chart = st.columns(2)
with left_chart:
    st.plotly_chart(movie_occupancy_chart(df), use_container_width=True)
with right_chart:
    st.plotly_chart(booked_available_chart(df), use_container_width=True)

# Show data table
st.subheader("📋 Show Details")
display_df = df.copy()
display_df["occupancy_pct"] = display_df["occupancy_pct"].map(lambda value: f"{value:.1f}%")
display_df = display_df.rename(columns={
    "show_id": "Show ID",
    "movie_name": "Movie",
    "show_time": "Show Time",
    "total_seats": "Total Seats",
    "booked_seats": "Booked Seats",
    "available_seats": "Available Seats",
    "occupancy_pct": "Occupancy"
})
st.dataframe(
    display_df[[
        "Show ID", "Movie", "Show Time", "Total Seats",
        "Booked Seats", "Available Seats", "Occupancy"
    ]],
    use_container_width=True,
    hide_index=True
)

# Update booked ticket count
st.subheader("✏️ Update Booked Tickets")
show_labels = {
    f'{row["show_id"]} | {row["movie_name"]} | {row["show_time"]}': row
    for row in get_shows()
}
selected_label = st.selectbox("Choose a show to update", list(show_labels.keys()))
selected_row = show_labels[selected_label]

with st.form("update_bookings_form"):
    updated_booked = st.number_input(
        "New booked ticket count",
        min_value=0,
        max_value=int(selected_row["total_seats"]),
        value=int(selected_row["booked_seats"])
    )
    update_submitted = st.form_submit_button("Update tickets")

    if update_submitted:
        try:
            update_booked_seats(selected_row["show_id"], int(updated_booked))
            st.success("Booked ticket count updated.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))

# CSV download
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered show data (CSV)",
    data=csv_data,
    file_name="cinema_occupancy.csv",
    mime="text/csv"
)

st.caption("Demo project • Data is stored in a local SQLite database.")

