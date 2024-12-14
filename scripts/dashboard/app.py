import os
import re
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State
import dash_table as dt
import psycopg2
from psycopg2 import OperationalError
from datetime import datetime

# Initialize Dash app
app = Dash(__name__)
server = app.server

# Initialize last_fetched_depth
last_fetched_depth = None

def create_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "host.docker.internal"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "welldb"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        return conn
    except OperationalError as e:
        print(f"Error: Unable to connect to the database: {e}")
        raise

def fetch_new_data(last_depth):
    """Fetch new rows from PostgreSQL database based on the last fetched depth."""
    try:
        conn = create_connection()
        cur = conn.cursor()
        date_suffix = datetime.now().strftime('%Y%m%d')
        table_name = f"petrophysics.petrophysics_{date_suffix}"
        if last_depth is None:
            query = f"SELECT * FROM {table_name} ORDER BY depth LIMIT 1000;"  # Adjust limit as needed
        else:
            query = f"SELECT * FROM {table_name} WHERE depth > {last_depth} ORDER BY depth LIMIT 1000;"  # Adjust limit as needed
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(data, columns=columns)
        cur.close()
        conn.close()
        # Replace -999.25 with NaN to treat as missing data
        df.replace(-999.25, pd.NA, inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def generate_frontpage():
    filename = "AREA-CONFIDENTIAL - Exploration Drilling"

    return html.Div(
        id="las-header",
        children=[
            html.Img(id="las-logo", src=app.get_asset_url("logo.png"), style={'height': '80px'}),
            html.Div(
                id="las-header-text",
                children=[
                    html.H1("Measuring While Drilling - Final Project Data Engineering"),
                    html.H1("Gian Antariksa"),
                    html.Div(
                        id="las-file-info",
                        children=[
                            html.Span(id="las-filename", children=filename, style={'fontSize': '20px', 'fontWeight': 'bold'}),
                            html.Span(
                                style={'fontSize': '16px', 'marginLeft': '10px'}
                            ),
                        ],
                    ),
                ],
            ),
            # Optional: Add Dash logo if needed
            # html.Img(id="dash-logo", src=app.get_asset_url("dash-logo.png")),
        ],
        style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'marginBottom': '40px'
        }
    )

def generate_axis_title(descr, unit):
    """Format axis title with line breaks and unit."""
    title_words = descr.split(" ")
    current_line = ""
    lines = []
    for word in title_words:
        if len(current_line) + len(word) > 15:
            lines.append(current_line.strip())
            current_line = ""
        current_line += f"{word} "
    lines.append(current_line.strip())
    title = "<br>".join(lines)
    title += f"<br>({unit})"
    return title

def generate_curves(df, height=950, width=1600, bg_color="white", font_size=10, tick_font_size=8, line_width=2):
    """
    Generate well logging curves layout similar to the reference script.
    """
    yvals = "depth"
    cols = df.columns.tolist()

    # Define curve descriptions and units
    # Replace the descriptions and units with actual values from your dataset
    curve_info = {
        "btvpvs": {"descr": "BAT YPVS Ratio", "unit": "1-3"},
        "dgrc": {"descr": "DGR Combined Gamma Ray", "unit": "gapi"},
        "ewxt": {"descr": "EWR Formation Eva Time", "unit": "hr"},
        "r15p": {"descr": "15in Phase Resistivity", "unit": "ohmm"},
        "r09p": {"descr": "R09P", "unit": "Units"},  # Replace with actual description if available
        "r27p": {"descr": "R27P", "unit": "Units"},  # Replace with actual description if available
        "r39p": {"descr": "R39P", "unit": "Units"},  # Replace with actual description if available
        "alcdlc": {"descr": "ALD LCRB Comp Density", "unit": "g/cc"},
        "aldclc": {"descr": "ALD LCRB Den Correction", "unit": "g/cc"},
        "tnps": {"descr": "CTN Porosity Sandstone", "unit": "pu"},
        "btcss": {"descr": "BAT Comp Shear Slowness", "unit": "us/f"},
        "btcs": {"descr": "BAT Comp Slowness", "unit": "us/f"},
    }

    # Define subplot structure similar to the reference script
    plots = [
        ["btvpvs", "dgrc"],                      # Subplot 1
        ["ewxt", "r15p", "r09p", "r27p", "r39p"], # Subplot 2
        ["alcdlc", "aldclc"],                     # Subplot 3
        ["tnps"],                                 # Subplot 4
        ["btcss", "btcs"]                         # Subplot 5
    ]

    # Define fixed X-axis ranges for each subplot
    xaxis_ranges = {
        1: [1, 3],     # Subplot 1: BAT YPVS Ratio
        2: [0, 1000],  # Subplot 2: 15in Phase Resistivity
        3: [0, 3.5],    # Subplot 3: ALD LCRB Comp Density
        4: [0, 50],     # Subplot 4: CTN Porosity Sandstone
        5: [50, 200],   # Subplot 5: BAT Comp Shear Slowness
    }

    # Create subplots
    fig = make_subplots(
        rows=1, cols=len(plots),
        shared_yaxes=True,
        horizontal_spacing=0.05,
    )

    # Define X-axis types for each subplot
    xaxis_types = ["linear", "log", "linear", "linear", "linear"]

    # Define line styles for specific curves
    line_styles = {
        "dgrc": {"dash": "solid"},
        "btvpvs": {"dash": "solid"},
        "ewxt": {"dash": "dash"},
        "r15p": {"dash": "dashdot"},
        "r09p": {"dash": "dashdot"},
        "r27p": {"dash": "dashdot"},
        "r39p": {"dash": "dashdot"},
        "alcdlc": {"dash": "dot"},
        "aldclc": {"dash": "dot"},
        "tnps": {"dash": "solid"},
        "btcss": {"dash": "dash"},
        "btcs": {"dash": "dashdot"},
    }

    # Iterate over each subplot and add corresponding traces
    for col_idx, plot_columns in enumerate(plots, start=1):
        for column in plot_columns:
            if column in cols and not df[column].isnull().all():
                fig.add_trace(
                    go.Scatter(
                        x=df[column],
                        y=df[yvals],
                        name=column.upper(),
                        line=dict(width=line_width, **line_styles.get(column, {"dash": "solid"})),
                        connectgaps=False  # Ensures lines are not drawn through missing data
                    ),
                    row=1, col=col_idx
                )
        # Update X-axis for the subplot
        first_column = plot_columns[0]
        if first_column in curve_info:
            descr = curve_info[first_column]["descr"]
            unit = curve_info[first_column]["unit"]
        else:
            descr = first_column.upper()
            unit = "Units"
        fig.update_xaxes(
            title=generate_axis_title(descr, unit),
            type=xaxis_types[col_idx - 1],
            range=xaxis_ranges[col_idx],
            showgrid=True,
            gridcolor='lightgray',
            row=1, col=col_idx
        )

    # Overlay additional X-axes on top for specific curves
    # Mapping of curves to their overlay axes with specified ranges and types
    overlay_axes_config = {
        "dgrc": {
            "overlaying": "x1",
            "anchor": "y",
            "side": "top",
            "title": generate_axis_title(curve_info["dgrc"]["descr"], curve_info["dgrc"]["unit"]),
            "type": "linear",
            "range": [0, 450],
            "position": 0.95,
        },
        "ewxt": {
            "overlaying": "x2",
            "anchor": "y",
            "side": "top",
            "title": generate_axis_title(curve_info["ewxt"]["descr"], curve_info["ewxt"]["unit"]),
            "type": "linear",  # Changed from "log" to "linear"
            "range": [0, 450],  # Adjusted range
            "position": 0.85,
        },
        "aldclc": {
            "overlaying": "x3",
            "anchor": "y",
            "side": "top",
            "title": generate_axis_title(curve_info["aldclc"]["descr"], curve_info["aldclc"]["unit"]),
            "type": "linear",
            "range": [-1.5, 1],
            "position": 0.75,
        },
        "btcs": {
            "overlaying": "x5",
            "anchor": "y",
            "side": "top",
            "title": generate_axis_title(curve_info["btcs"]["descr"], curve_info["btcs"]["unit"]),
            "type": "linear",
            "range": [40, 140],
            "position": 0.65,
        },
    }

    # Add overlay X-axes to the layout
    for curve, config in overlay_axes_config.items():
        # Calculate the new axis number
        overlay_axis_num = len(plots) + list(overlay_axes_config.keys()).index(curve) + 1
        # Determine which subplot the curve belongs to
        for subplot_idx, plot_columns in enumerate(plots, start=1):
            if curve in plot_columns:
                main_subplot = subplot_idx
                break
        else:
            main_subplot = 1  # Default to subplot 1 if not found

        fig.update_layout({
            f'xaxis{overlay_axis_num}': dict(
                overlaying=config["overlaying"],
                anchor=config["anchor"],
                side=config["side"],
                title=config["title"],
                type=config["type"],
                range=config["range"],
                position=config["position"],
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linecolor='black',
                linewidth=1,
                mirror=True,
                automargin=True,
                titlefont=dict(family="Arial, sans-serif", size=font_size),
                tickfont=dict(family="Arial, sans-serif", size=tick_font_size),
            )
        })
        # Assign the specific X-axis to the corresponding trace
        for trace in fig.data:
            if trace.name.lower() == curve:
                trace.update(xaxis=f'x{overlay_axis_num}')

    # Y-axis configuration
    y_descr = "Depth"
    y_unit = "meters"
    fig.update_yaxes(
        # title=generate_axis_title(y_descr, y_unit),
        range=[9000, 8300],
        title_font=dict(size=font_size),
        tickfont=dict(size=tick_font_size),
        autorange="reversed",
        showgrid=True,
        gridcolor='lightgray',
        mirror=True,
        showline=True,
        linecolor='black',
        linewidth=1,
    )

    # Update overall layout
    fig.update_layout(
        height=height,
        width=width,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        hovermode="y unified",
        legend={"font": {"size": tick_font_size}},
        margin=go.layout.Margin(r=100, t=100, b=50, l=80, autoexpand=False),
    )

    # Style all main X-axes
    for i in range(1, len(plots)+1):
        fig.update_xaxes(
            mirror=True,
            showline=True,
            linecolor='black',
            linewidth=1,
            title_font=dict(size=font_size),
            tickfont=dict(size=tick_font_size),
            row=1, col=i
        )

    # Style overlay X-axes
    for i in range(len(plots)+1, len(plots)+1+len(overlay_axes_config)):
        fig.update_xaxes(
            showgrid=True,
            gridcolor='lightgray',
            mirror=True,
            showline=True,
            linecolor='black',
            linewidth=1,
            title_font=dict(size=font_size),
            tickfont=dict(size=tick_font_size),
        )

    return dcc.Graph(figure=fig)

def generate_table(df):
    if df.empty:
        return html.Div("Waiting for data to populate...")

    # Adjust based on actual DataFrame structure
    # Example assumes columns: 'mnemonic', 'descr', 'unit', 'value'
    required_columns = ["mnemonic", "descr", "unit", "value"]
    if not all(col in df.columns for col in required_columns):
        # Create a sample DataFrame if required columns are missing
        sample_data = {
            "mnemonic": ["DT", "RHOB", "NPHI"],
            "descr": ["Delta Time", "Bulk Density", "Neutron Porosity"],
            "unit": ["us/ft", "g/cc", "fraction"],
            "value": [120.5, 2.35, 0.15],
        }
        df = pd.DataFrame(sample_data)
    else:
        # Select and rename columns for display
        df = df[required_columns]
        # Replace NaN with empty strings for display purposes
        df['value'] = df['value'].fillna('')

    return dt.DataTable(
        id="table",
        columns=[{"name": col.upper(), "id": col} for col in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_action='none',  # Disable pagination
        style_table={'overflowX': 'auto'},  # Removed maxHeight and overflowY
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'minWidth': '100px',
            'width': '150px',
            'maxWidth': '180px',
            'whiteSpace': 'normal'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
    )

def generate_statistics(df):
    if df.empty:
        return html.Div("Statistics will be displayed when data is available.")
    stats = df.describe()
    return html.Div(
        children=[
            html.H4("Statistics"),
            html.Table(
                # Header
                [html.Tr([html.Th("Statistic")] + [html.Th(col.upper()) for col in stats.columns])] +
                # Body
                [
                    html.Tr([html.Td(stat)] + [html.Td(f"{stats.loc[stat, col]:.2f}") for col in stats.columns])
                    for stat in stats.index
                ],
                style={
                    'width': '100%',
                    'border': '1px solid black',
                    'borderCollapse': 'collapse',
                    'textAlign': 'center'
                },
                className="statistics-table"
            ),
        ],
        style={'padding': '20px'}
    )

# Define the layout of the app with dcc.Store for data accumulation
app.layout = html.Div(
    [
        # Store component to hold all accumulated data
        dcc.Store(id='stored-data', data=[], storage_type='memory'),

        html.Div(id="controls", children=[html.Button("Refresh", id="refresh-button")], style={'marginBottom': '20px'}),
        html.Div(id="frontpage", className="page", children=generate_frontpage()),
        dcc.Interval(id="interval-component", interval=500, n_intervals=0),
        html.Div(
            className="section",
            style={'marginBottom': '40px'},
            children=[
                html.Div(
                    className="section-title", 
                    style={
                        'marginBottom': '20px',
                        'padding': '10px',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    },
                    children="LAS Data Table"
                ),
                html.Div(id="las-table"),
            ],
        ),
        html.Div(
            className="section",
            style={
                'marginTop': '40px',
                'marginBottom': '40px',
                'padding': '20px 0'
            },
            children=[
                html.Div(
                    className="section-title", 
                    style={
                        'marginBottom': '30px',
                        'padding': '10px',
                        'backgroundColor': '#f8f9fa',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    },
                    children="LAS Curves"
                ),
                html.Div(id="las-curves", style={'paddingTop': '20px'}),
            ],
        ),
        html.Div(
            className="section",
            style={'marginTop': '40px'},
            children=[
                html.Div(
                    className="section-title", 
                    style={
                        'marginBottom': '20px',
                        'padding': '10px',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    },
                    children="Statistics"
                ),
                html.Div(id="statistics"),
            ],
        ),
    ],
    style={'padding': '20px'}
)

@app.callback(
    [
        Output("stored-data", "data"),
        Output("las-table", "children"),
        Output("las-curves", "children"),
        Output("statistics", "children")
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("refresh-button", "n_clicks")
    ],
    [
        State("stored-data", "data")
    ]
)
def update_dashboard(n_intervals, n_clicks, stored_data):
    global last_fetched_depth
    # Fetch new data
    new_data = fetch_new_data(last_fetched_depth)
    if not new_data.empty:
        last_fetched_depth = new_data["depth"].max()
        if stored_data:
            # Convert stored_data back to DataFrame
            all_data = pd.DataFrame(stored_data)
            # Append new data
            all_data = pd.concat([all_data, new_data], ignore_index=True)
            # Drop duplicates based on 'depth' if necessary
            all_data = all_data.drop_duplicates(subset='depth', keep='last')
        else:
            all_data = new_data
    else:
        if stored_data:
            all_data = pd.DataFrame(stored_data)
        else:
            all_data = pd.DataFrame()

    # Filter data within the desired depth range
    desired_min_depth = 7500
    desired_max_depth = 11000
    if not all_data.empty:
        all_data = all_data[(all_data['depth'] >= desired_min_depth) & (all_data['depth'] <= desired_max_depth)]

    # Convert accumulated data to dict
    accumulated_data = all_data.to_dict('records')

    return (
        accumulated_data,               # Update stored-data
        generate_table(all_data),        # Update table
        generate_curves(all_data),       # Update curves
        generate_statistics(all_data)    # Update statistics
    )

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
