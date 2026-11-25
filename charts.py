import pandas as pd
import plotly.express as px


def prepare_dataframe(records):
    """Convert database records to a DataFrame and calculate derived values."""
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["available_seats"] = df["total_seats"] - df["booked_seats"]
    df["occupancy_pct"] = (
        df["booked_seats"] / df["total_seats"] * 100
    ).round(1)
    return df


def movie_occupancy_chart(df):
    """Show occupancy percentage for each movie."""
    movie_df = (
        df.groupby("movie_name", as_index=False)
        .agg(
            total_seats=("total_seats", "sum"),
            booked_seats=("booked_seats", "sum")
        )
    )
    movie_df["occupancy_pct"] = (
        movie_df["booked_seats"] / movie_df["total_seats"] * 100
    ).round(1)

    fig = px.bar(
        movie_df,
        x="movie_name",
        y="occupancy_pct",
        text="occupancy_pct",
        labels={
            "movie_name": "Movie",
            "occupancy_pct": "Occupancy (%)"
        },
        title="Movie-wise Ticket Occupancy",
        range_y=[0, 100]
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(margin=dict(t=60, b=20), yaxis_ticksuffix="%")
    return fig


def booked_available_chart(df):
    """Show booked and available seats as a pie chart."""
    booked = int(df["booked_seats"].sum())
    available = int(df["available_seats"].sum())

    pie_df = pd.DataFrame({
        "Seat status": ["Booked", "Available"],
        "Seats": [booked, available]
    })

    fig = px.pie(
        pie_df,
        names="Seat status",
        values="Seats",
        hole=0.45,
        title="Booked vs Available Seats"
    )
    fig.update_traces(textinfo="label+value+percent")
    return fig
