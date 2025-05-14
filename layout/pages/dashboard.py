from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from dash import html
import datetime
from app_data import get_available_school_years
available_years=get_available_school_years()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
dcc.Store(id="stored_school_years", data=get_available_school_years())  # Store available years

def get_greeting():
    today = datetime.datetime.today()
    day_of_week = today.strftime('%A')  # Get the current day
    formatted_date = today.strftime('%B %d, %Y')  # Format the date as Month Day, Year
    
    # Determine the time of day and create a corresponding greeting
    hour = today.hour
    if 5 <= hour < 12:
        time_of_day = "Morning"
    elif 12 <= hour < 17:
        time_of_day = "Afternoon"
    else:
        time_of_day = "Evening"
    
    return html.Div([
        html.P(f" {formatted_date} ({day_of_week})", style={'fontWeight': 'bold', 'color': '#5c7dad'}),
        html.P(f" Good {time_of_day}, Admin! Stay updated with the latest data and trends.", style={'color': '#0a4485'}),
    ])

def dashboard_content(data, grade_options, region_options):
    no_border_style = {
        "border": "none",
        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    }

    sticky_card_style = {
        **no_border_style,
        "padding": "10px",
        "borderRadius": "10px",
        "position": "sticky",
        "top": "30px",
        "zIndex": "1000"
    }

    return dbc.Container(
        fluid=True,
        children=[
            html.H1("Dashboard", className="page-title"),
            get_greeting(), 
            html.Div(id='kpi_card_row', className='mb-4'),

            html.Div("Filter Control Panel", style={
                "fontWeight": "600", "fontSize": "18px",
                "color": "#343a40", "paddingLeft": "10px"
            }),
            dbc.Card(
                [dbc.CardBody(
                    dbc.Row([
                        dbc.Col([
                            html.Label("School Year:"),
                            dcc.Dropdown(
                                id='school_year_filter',
                                value="2023-2024",
                                options=[{'label': y, 'value': y} for y in get_available_school_years()],
                                placeholder="Select School Year",
                                clearable=False  # ← important to prevent None
                            )

                        ], width=2),

                        dbc.Col([
                            html.Label("Region:"),
                            dcc.Dropdown(id='region_filter', options=region_options, multi=True)
                        ], width=2),

                        dbc.Col([
                            html.Label("Grade Level:"),
                            dcc.Dropdown(id='grade_filter', options=grade_options, multi=True)
                        ], width=2),

                        dbc.Col([
                            html.Label("Gender:"),
                            dcc.RadioItems(
                                id='gender_filter',
                                options=[
                                    {'label': 'Male', 'value': 'Male'},
                                    {'label': 'Female', 'value': 'Female'},
                                    {'label': 'All', 'value': 'All'}
                                ],
                                value='All',
                                inline=True,
                                labelStyle={'marginRight': '10px'}
                            )
                        ], width=2),

                        dbc.Col([
                            html.Label("Search School:"),
                            dcc.Dropdown(
                            id='school_search',
                            options=[],
                            placeholder='Search...',
                            className='multiline-dropdown centered-placeholder',
                            optionHeight=50,
                            style={
                                'width': '100%',
                                'minWidth': '300px',
                                'whiteSpace': 'normal',
                                'overflowWrap': 'break-word',
                                'textAlign': 'justify'
                            }
                            ),
                            html.Br(),
                            dbc.Modal(
                                id='school_modal',
                                is_open=False,
                                children=[
                                    dbc.ModalHeader(dbc.ModalTitle(id='modal_school_name')),
                                    dbc.ModalBody(id='modal_school_body'),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close_btn", className="ms-auto", n_clicks=0)
                                    )
                                ]
                            )
                        ], width=4),
                    ])
                )],
                style={**sticky_card_style, 
                       "boxShadow": "none", 
                       "transition": "none", 
                       "transform": "none",
                       "paddingBottom": "0px"},  # Remove padding at the bottom
                className="mb-4 shadow-sm"
            ),


            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='enrollment_choropleth_map', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "600px"}),
                    width=8, className="mb-4"
                ),

                dbc.Col([
                    dcc.Loading(html.Div(id='most_enrolled_division_card', className='mb-4')),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='gender_pie_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"})
                ], width=4, className="mb-4")
            ]),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='enrollment_vs_schools_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style=no_border_style),
                    width=12, className="mb-4"
                )
            ]),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='top_schools_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=6, className="mb-4"
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='shs_track_bar_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=6, className="mb-4"
                )
            ]),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='k_to_12_distribution_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style=no_border_style),
                    width=12
                )
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='enrollment_trend_line_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=7
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='transition_rate_chart', config={'displayModeBar': False}, style={'height': '100%', 'width':'100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=5
                )
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='coc_sector_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=6, className="mb-4"
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='sned_sector_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style={**no_border_style, "height": "400px"}),
                    width=6, className="mb-4"
                )
            ]),
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Loading(dcc.Graph(id='up_sned_sector_chart', config={'displayModeBar': False}, style={'height': '100%'}))
                        ])
                    ], style=no_border_style),
                    width=12
                )
            ], className="mb-4"),
        ]
    )