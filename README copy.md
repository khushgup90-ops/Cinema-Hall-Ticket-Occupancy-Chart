# Cinema Hall Ticket Occupancy Chart

A beginner-friendly Python web dashboard built with Streamlit, Pandas, Plotly and SQLite.

## Features
- Total, booked and available seat metrics
- Automatic occupancy percentage
- Movie and show-time filters
- Movie-wise bar chart
- Booked vs available pie chart
- Add new movie shows
- Update booked ticket counts
- SQLite database storage
- CSV export

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The SQLite database (`cinema.db`) is created automatically and populated with sample data on the first run.
