
import dash_bootstrap_components as dbc
from dash import html, dcc

def manage_data_content(region_options, grade_options):
    return dbc.Container([
        html.H1("Manage Data Page", className="page-title"),
        html.H3("Add New Enrollment Record", className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Region"),
                dcc.Dropdown(id='input_region', options=region_options, placeholder="Select Region")
            ]),
            dbc.Col([
                dbc.Label("Division"),
                dcc.Dropdown(id='input_division', options=[], placeholder="Select Division", disabled=True)
            ])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("School Name"),
                dcc.Dropdown(id='input_school_name', options=[], placeholder="Search School", searchable=True, disabled=True)
            ])
        ], className="mb-3"),

        dbc.Card([
            dbc.CardHeader("Auto-Filled School Information"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("BEIS School ID"),
                        dbc.Input(id='beis_school_id_display', type="text", disabled=True)
                    ]),
                    dbc.Col([
                        dbc.Label("Barangay"),
                        dbc.Input(id='auto_barangay', type="text", disabled=True)
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Sector"),
                        dbc.Input(id='auto_sector', type="text", disabled=True)
                    ]),
                    dbc.Col([
                        dbc.Label("School Subclassification"),
                        dbc.Input(id='auto_subclassification', type="text", disabled=True)
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("School Type"),
                        dbc.Input(id='auto_type', type="text", disabled=True)
                    ]),
                    dbc.Col([
                        dbc.Label("Modified COC"),
                        dbc.Input(id='auto_coc', type="text", disabled=True)
                    ])
                ])
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Label("School Year"),
                dcc.Input(id='input_school_year', type='text', placeholder="e.g., 2024-2025", className="form-control")
            ]),
            dbc.Col([
                dbc.Label("Grade Level"),
                dcc.Dropdown(id='input_grade', options=grade_options, placeholder="Select Grade")
            ])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("Gender"),
                dcc.RadioItems(
                    id='input_gender',
                    options=[
                        {'label': 'Male', 'value': 'Male'},
                        {'label': 'Female', 'value': 'Female'}
                    ],
                    inline=True,
                    labelStyle={'margin-right': '15px'}
                )

            ]),
            dbc.Col([
                dbc.Label("Enrollment Count"),
                dcc.Input(id='input_enrollment', type='number', placeholder="Enter Enrollment Count", className="form-control")
            ])
        ], className="mb-4"),

        dbc.Button("Submit", id="submit_button", color="primary", className="mb-3"),
        html.Div(id="submission_feedback", className="text-success")
    ])
