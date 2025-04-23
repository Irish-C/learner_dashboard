from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import plotly.express as px
import pandas as pd

correct_region_order = [
    'CAR', 'NCR', 'Region I', 'Region II', 'Region III', 'Region IV-A',
    'MIMAROPA', 'Region V', 'Region VI', 'Region VII', 'Region VIII',
    'Region IX', 'Region X', 'Region XI', 'Region XII', 'CARAGA', 'BARMM'
]

def dashboard_content(data, grade_options, region_options, combined_shs_track_df):
    return dbc.Container(
        fluid=True,
        children=[
            html.H1("Dashboard", className="page-title"),
            html.P("Welcome Back, Teacher!", className="subtitle"),
            html.Br(),

            # ✅ KPI Cards (dynamic via callback)
            html.Div(id='kpi_card_row', className='mb-4'),
            # ✅ Row-based Filter Panel (new layout)
            html.Div("Filter Control Panel", style={
                "fontWeight": "600",
                "fontSize": "18px",
                "color": "#343a40",
                "paddingLeft": "10px"
            }),
            dbc.Card(
             [dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        html.Label("School Year:"),
                        dcc.Dropdown(
                            id='school_year_filter',
                            options=[{'label': sy, 'value': sy} for sy in sorted(data['School Year'].unique(), reverse=True)],
                            value=sorted(data['School Year'].unique(), reverse=True)[0],
                            placeholder='Select School Year'
                        )
                    ], width=2),

                    dbc.Col([
                        html.Label("Region:"),
                        dcc.Dropdown(
                            id='region_filter',
                            options=region_options,
                            multi=True,
                            placeholder='Select Region'
                        )
                    ], width=2),

                    dbc.Col([
                        html.Label("Grade Level:"),
                        dcc.Dropdown(
                            id='grade_filter',
                            options=grade_options,
                            multi=True,
                            placeholder='Select Grade Level'
                        )
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
                            labelStyle={'margin-right': '10px'}
                        )
                    ], width=2),

                    dbc.Col([
                        html.Label("Search School:"),
                        dcc.Dropdown(
                            id='school_search',
                            options=[],
                            placeholder='Search by School ID or Name',
                            searchable=True
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
                ], className="g-3")
            )
        ],
        className="mb-4 shadow-sm no-hover",
        style={"padding": "10px", 
               "borderRadius": "10px", 
                "position": "sticky",
                "top": "30px", 
                "zIndex": "1000",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
               }),


            # ✅ Charts & Tabs
                    # First Row
                    dbc.Row([
                        # First column with the first card (graph)
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='enrollment_choropleth_map',
                                        config={'displayModeBar': False},
                                        style={'height': '100%'}
                                    ))
                                ])
                            ], style={'height': '600px'}),  # Set height of the card
                            width=8,  # Take up 8 out of 12 columns
                            className="mb-4"
                        ),
    
                        # Second column with two cards (one for division and one for pie chart)
                        dbc.Col(
                            [
                                # First card for "most enrolled division"
                                dcc.Loading(
                                    html.Div(id='most_enrolled_division_card', className='mb-4'),
                                    type='default'
                                ),
                                # Second card for the pie chart
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Loading(
                                            dcc.Graph(
                                                id='gender_pie_chart',
                                                config={'displayModeBar': False},
                                                style={'height': '100%'}
                                            ),
                                            type='default'
                                        )
                                    ])
                                ], style={'height': '400px'})  # Set height of the pie chart card
                            ],
                            width=4,  # Take up 4 out of 12 columns
                            className="mb-4"
                        )
                    ]),

                    # 2nd Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='enrollment_vs_schools_chart',
                                        config={'displayModeBar': False},
                                        style={'height': '100%'}
                                        ))
                                ])
                            ]),
                            width=12,
                            className="mb-4"
                            )
                    ]),

                    # 3rd Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='top_schools_chart'
                                    ))
                            ])
                        ]),
                        width=6,
                        className="mb-4"
                    ),
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='shs_track_bar_chart'
                                    ))
                            ])
                        ]),
                        width=6,
                        className="mb-4"
                    )
                    ]),

                    # 4th Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(
                                        dcc.Graph(id='k_to_12_distribution_chart'),
                                        type='default'
                                    )
                                ])
                            ]),
                            width=12
                        ),
                    ], className="mb-4"),

                    # 5th Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(
                                        dcc.Graph(id='transition_rate_chart'),
                                        type='default'
                                    )
                                ])
                            ]),
                            width=12
                        )
                    ], className="mb-4"),

                    # 6th Row
                    dbc.Row([
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='coc_sector_chart',
                                        config={'displayModeBar': False},
                                        style={'height': '100%'}
                                    ))
                                ])
                            ], style={'height': '400px'}),
                            width=6,
                            className="mb-4"
                        ),
                        
                        dbc.Col(
                            dbc.Card([
                                dbc.CardBody([
                                    dcc.Loading(dcc.Graph(
                                        id='sned_sector_chart',
                                        config={'displayModeBar': False},
                                        style={'height': '100%'}
                                    ))
                                ])
                            ], style={'height': '400px'}),
                            width=6,
                            className="mb-4"
                    )
                    ]),
])
