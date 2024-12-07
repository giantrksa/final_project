# apps/dash-lastodash/lastodash.py

import os
import pandas as pd
import psycopg2
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output
from dash import dcc, html, dash_table as dt
import pathlib

# Initialize Dash app
app = dash.Dash(__name__)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.resolve()

# Database connection parameters
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres_dw')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

def get_db_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    return conn

def fetch_las_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM las_data ORDER BY DEPT ASC", conn)
    conn.close()
    return df

def generate_frontpage():
    return html.Div(
        id="las-header",
        children=[
            html.Img(id="las-logo", src=app.get_asset_url("logo.png")),
            html.Div(
                id="las-header-text",
                children=[
                    html.H1("LAS Report"),
                    html.Div(
                        id="las-file-info",
                        children=[
                            html.Span(id="las-filename", children="Real-Time LAS Data"),
                            html.Span(" (Streaming Version)"),
                        ],
                    ),
                ],
            ),
            html.Img(id="dash-logo", src=app.get_asset_url("dash-logo.png")),
        ],
    )

def generate_curves(df, height=700, width=1000, bg_color="white", font_size=10, tick_font_size=8, line_width=2):
    # Define the curves to plot
    curves = ['DT', 'RHOB', 'NPHI', 'GR']  # Update based on your LAS data
    yvals = "DEPT"

    fig = go.Figure()

    for curve in curves:
        if curve in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df[curve],
                    y=df[yvals],
                    mode='lines',
                    name=curve,
                    line=dict(width=line_width)
                )
            )

    fig.update_layout(
        height=height,
        width=width,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        hovermode="y",
        legend={"font": {"size": tick_font_size}},
        margin=go.layout.Margin(r=100, t=100, b=50, l=80, autoexpand=False),
        yaxis=dict(title="Depth (m)", autorange='reversed'),
        xaxis=dict(title="Measurement Value")
    )

    return dcc.Graph(figure=fig)

def generate_table(df):
    return dt.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
        filter_action="native",
        page_action="native",
        page_current=0,
        page_size=20,
        style_table={'overflowX': 'auto'},
        style_cell={
            'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        }
    )

app.layout = html.Div(
    [
        html.Div(id="controls", children=[html.Button("Print", id="las-print")]),
        html.Div(id="frontpage", className="page", children=generate_frontpage()),
        html.Div(
            className="section",
            children=[
                html.Div(className="section-title", children="LAS well"),
                html.Div(
                    className="page",
                    children=[
                        html.Div(id="las-table", children=[]),
                        html.Div(id="las-table-print"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="section",
            children=[
                html.Div(className="section-title", children="LAS curves"),
                html.Div(
                    className="page",
                    children=[html.Div(id="las-curves", children=[])],
                ),
            ],
        ),
        # Interval component for real-time updates
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        )
    ]
)

@app.callback(
    [Output('las-curves', 'children'),
     Output('las-table', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = fetch_las_data()
    curves = generate_curves(df)
    table = generate_table(df)
    return curves, table

@app.callback(Output("las-table-print", "children"), [Input("table", "data")])
def update_table_print(data):
    # Same as before
    colwidths = {
        "mnemonic": "100px",
        "descr": "300px",
        "unit": "25px",
        "value": "300px",
    }
    if not data:
        return []
    tables_list = []
    num_tables = int(len(data) / 34) + 1  # 34 rows max per page
    for i in range(num_tables):
        table_rows = []
        for j in range(34):
            if i * 34 + j >= len(data):
                break
            table_rows.append(
                html.Tr([html.Td(data[i * 34 + j].get(key, "")) for key in data[0].keys()])
            )
        table_rows.insert(
            0,
            html.Tr(
                [
                    html.Th(key.title(), style={"width": colwidths.get(key, "100px")})
                    for key in data[0].keys()
                ]
            ),
        )
        tables_list.append(
            html.Div(className="tablepage", children=html.Table(table_rows))
        )
    return tables_list

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
