import streamlit as st
import pandas as pd

from background import add_scroll_sky

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


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CinemaX | Occupancy Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
add_scroll_sky()


# ==========================================
# CUSTOM CSS - PREMIUM CINEMA THEME
# ==========================================

st.markdown(
    """
    <style>

    /* Main background */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(124, 58, 237, 0.15),
                transparent 35%
            ),
            #09090f;

        color: #f8fafc;
    }

    /* Main container */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #11111b;
        border-right: 1px solid #27273a;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff;
    }

    /* Main heading */

    .cinema-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .cinema-title span {
        background: linear-gradient(
            90deg,
            #a855f7,
            #6366f1,
            #38bdf8
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .cinema-subtitle {
        color: #9ca3af;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Dashboard cards */

    div[data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #171725,
            #11111b
        );

        border: 1px solid #29293d;
        border-radius: 18px;

        padding: 22px 20px;

        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);

        transition: all 0.25s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #8b5cf6;
        transform: translateY(-3px);
    }

    div[data-testid="stMetricLabel"] {
        color: #a5a5b5;
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 30px;
        font-weight: 700;
    }

    /* Section headings */

    h2, h3 {
        color: #f8fafc !important;
    }

    /* Input fields */

    .stTextInput input,
    .stNumberInput input {
        background-color: #171725 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #34344b !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #171725;
        border-color: #34344b;
        border-radius: 10px;
    }

    /* Buttons */

    .stButton button,
    .stFormSubmitButton button {
        background: linear-gradient(
            90deg,
            #7c3aed,
            #6366f1
        );

        color: white;
        border: none;
        border-radius: 10px;

        font-weight: 600;

        padding: 10px 18px;

        transition: all 0.2s ease;
    }

    .stButton button:hover,
    .stFormSubmitButton button:hover {
        border: none;
        box-shadow: 0 0 18px rgba(139, 92, 246, 0.4);
        transform: translateY(-2px);
    }

    /* Progress bar */

    div[data-testid="stProgress"] > div > div {
        background: linear-gradient(
            90deg,
            #7c3aed,
            #38bdf8
        );
    }

    /* Data table */

    div[data-testid="stDataFrame"] {
        border: 1px solid #29293d;
        border-radius: 14px;
        overflow: hidden;
    }

    /* Divider */

    hr {
        border-color: #29293d;
    }

    /* Footer */

    .cinema-footer {
        text-align: center;
        color: #77778c;
        font-size: 13px;
        padding-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

initialize_database()


# ==========================================
# HEADER
# ==========================================

st.markdown(
    """
    <div class="cinema-title">
        🎬 Cinema<span>X</span>
    </div>

    <div class="cinema-subtitle">
        Smart Cinema Management & Ticket Occupancy Analytics
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# LOAD DATA
# ==========================================

all_records = get_shows()

all_df = prepare_dataframe(all_records)


if all_df.empty:

    st.warning("No cinema shows available. Please add a show.")

    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🎥 Cinema Control")

    st.caption("Manage your cinema hall")

    st.divider()

    st.subheader("🔎 Dashboard Filters")

    movie_options = [
        "All Movies"
    ] + sorted(
        all_df["movie_name"].unique().tolist()
    )

    selected_movie = st.selectbox(
        "Select Movie",
        movie_options,
    )

    time_options = [
        "All Show Times"
    ] + sorted(
        all_df["show_time"].unique().tolist()
    )

    selected_time = st.selectbox(
        "Select Show Time",
        time_options,
    )

    st.divider()

    st.subheader("➕ Add New Movie Show")

    with st.form(
        "add_show_form",
        clear_on_submit=True,
    ):

        new_movie = st.text_input(
            "Movie Name",
            placeholder="Enter movie name",
        )

        new_time = st.selectbox(
            "Show Timing",
            [
                "09:00 AM",
                "10:00 AM",
                "11:00 AM",
                "01:00 PM",
                "02:00 PM",
                "03:00 PM",
                "06:00 PM",
                "09:00 PM",
            ],
        )

        new_total = st.number_input(
            "Total Seats",
            min_value=1,
            max_value=2000,
            value=150,
        )

        new_booked = st.number_input(
            "Already Booked Seats",
            min_value=0,
            max_value=int(new_total),
            value=0,
        )

        add_button = st.form_submit_button(
            "➕ Add Movie Show",
            use_container_width=True,
        )

        if add_button:

            try:

                add_show(
                    new_movie,
                    new_time,
                    int(new_total),
                    int(new_booked),
                )

                st.success(
                    f"{new_movie} added successfully!"
                )

                st.rerun()

            except ValueError as error:

                st.error(str(error))


# ==========================================
# APPLY FILTERS
# ==========================================

df = all_df.copy()


if selected_movie != "All Movies":

    df = df[
        df["movie_name"] == selected_movie
    ]


if selected_time != "All Show Times":

    df = df[
        df["show_time"] == selected_time
    ]


if df.empty:

    st.warning(
        "No shows found for the selected filters."
    )

    st.stop()


# ==========================================
# CALCULATE DASHBOARD DATA
# ==========================================

total_seats = int(
    df["total_seats"].sum()
)

booked_seats = int(
    df["booked_seats"].sum()
)

available_seats = int(
    df["available_seats"].sum()
)


if total_seats > 0:

    occupancy = (
        booked_seats / total_seats
    ) * 100

else:

    occupancy = 0


# ==========================================
# KPI CARDS
# ==========================================

st.markdown("## 📊 Overview")

st.caption(
    "Real-time summary of cinema ticket occupancy"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="🎟️ Total Seats",
        value=f"{total_seats:,}",
    )


with col2:

    st.metric(
        label="🟣 Booked Tickets",
        value=f"{booked_seats:,}",
    )


with col3:

    st.metric(
        label="🟢 Available Seats",
        value=f"{available_seats:,}",
    )


with col4:

    st.metric(
        label="📈 Occupancy Rate",
        value=f"{occupancy:.1f}%",
    )


# ==========================================
# OCCUPANCY PROGRESS
# ==========================================

st.markdown("### 🎯 Hall Occupancy")

st.progress(
    min(occupancy / 100, 1.0)
)

st.caption(
    f"{booked_seats:,} out of "
    f"{total_seats:,} seats are booked "
    f"({occupancy:.1f}%)"
)


st.divider()


# ==========================================
# CHARTS
# ==========================================

st.markdown("## 📈 Occupancy Analytics")

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.plotly_chart(
        movie_occupancy_chart(df),
        use_container_width=True,
    )


with chart_col2:

    st.plotly_chart(
        booked_available_chart(df),
        use_container_width=True,
    )


st.divider()


# ==========================================
# SHOW DETAILS TABLE
# ==========================================

st.markdown("## 🎬 Movie Show Details")

st.caption(
    "Complete information about available cinema shows"
)


display_df = df.copy()


display_df["occupancy_pct"] = (
    display_df["occupancy_pct"].map(
        lambda value: f"{value:.1f}%"
    )
)


display_df = display_df.rename(
    columns={
        "show_id": "Show ID",
        "movie_name": "Movie Name",
        "show_time": "Show Timing",
        "total_seats": "Total Seats",
        "booked_seats": "Booked Seats",
        "available_seats": "Available Seats",
        "occupancy_pct": "Occupancy",
    }
)


st.dataframe(
    display_df[
        [
            "Show ID",
            "Movie Name",
            "Show Timing",
            "Total Seats",
            "Booked Seats",
            "Available Seats",
            "Occupancy",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


st.divider()


# ==========================================
# UPDATE BOOKED TICKETS
# ==========================================

st.markdown("## ✏️ Update Ticket Bookings")

st.caption(
    "Update the number of booked tickets for any show"
)


show_records = get_shows()


show_labels = {
    (
        f'{row["show_id"]} | '
        f'{row["movie_name"]} | '
        f'{row["show_time"]}'
    ): row

    for row in show_records
}


if show_labels:

    selected_label = st.selectbox(
        "Choose Movie Show",
        list(show_labels.keys()),
    )

    selected_row = show_labels[
        selected_label
    ]


    with st.form(
        "update_bookings_form"
    ):

        updated_booked = st.number_input(
            "New Booked Ticket Count",
            min_value=0,
            max_value=int(
                selected_row["total_seats"]
            ),
            value=int(
                selected_row["booked_seats"]
            ),
        )


        update_button = st.form_submit_button(
            "💾 Update Bookings"
        )


        if update_button:

            try:

                update_booked_seats(
                    selected_row["show_id"],
                    int(updated_booked),
                )

                st.success(
                    "Ticket bookings updated successfully!"
                )

                st.rerun()

            except ValueError as error:

                st.error(str(error))


st.divider()


# ==========================================
# CSV DOWNLOAD
# ==========================================

st.markdown("## 📥 Export Data")


csv_data = df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Occupancy Report",
    data=csv_data,
    file_name="cinema_occupancy_report.csv",
    mime="text/csv",
)


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="cinema-footer">

        CinemaX Dashboard<br>

        Built with Python • Streamlit • Pandas • Plotly • SQLite

    </div>
    """,
    unsafe_allow_html=True,
)