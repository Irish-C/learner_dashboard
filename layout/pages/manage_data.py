
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from app_data import get_available_school_years
available_years = get_available_school_years()

def manage_data_content(region_options, grade_options, school_year_options):
    return dbc.Container([
        html.H1("Manage Data", className="page-title mb-4"),
        html.H3("Add New Enrollment Record", className="mb-4"),
         # Upload CSV Button and Modal
        dbc.Button("📤 Upload CSV", id="open-upload-modal", color="primary", className="mb-4"), 
        dbc.Modal([
            dbc.ModalHeader("Upload Enrollment Data CSV"),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col([html.Label("Select School Year"),
                        dcc.Dropdown(
                            id='upload-school-year-dropdown',
                            options=[{'label': f"{y}-{y+1}", 'value': f"{y}-{y+1}"} for y in range(2015, 2031)],
                            placeholder="Select School Year",
                            value="2023-2024"
                        )]
                    )
                ], className="mb-3"),

                dcc.Upload(
                    id='upload-data',
                    children=html.Div(['📁 Drag and Drop or ', html.A('Click to Select File')]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'marginBottom': '15px'
                    },
                    multiple=False
                ),
                
                # Display filename after upload
                html.Div(id="upload-filename", style={'fontSize': 18, 'fontWeight': 'bold'}),

                html.Div(id='upload-feedback', style={'fontWeight': 'bold'}),
                dcc.Store(id='refresh_school_year_trigger', data='initial-load')
            ]),

            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-upload-modal", className="ms-auto", color="secondary"),
                dbc.Button("Submit", id="submit-upload", color="primary")
            ])
        ], id="upload-modal", is_open=False),
        dbc.Row([
            dbc.Col([
                dbc.Label("Region"),
                dcc.Dropdown(id='input_region', options=region_options, placeholder="Select Region")
            ], width=6),
            dbc.Col([
                dbc.Label("Division"),
                dcc.Dropdown(id='input_division', options=[], placeholder="Select Division", disabled=True)
            ], width=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Label("School Name"),
                dcc.Dropdown(id='input_school_name', options=[], placeholder="Search School", searchable=True, disabled=True)
            ])
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Auto-Filled School Information", className="fw-bold"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("BEIS School ID"),
                        dbc.Input(id='beis_school_id_display', type="text", disabled=True)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Barangay"),
                        dbc.Input(id='auto_barangay', type="text", disabled=True)
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Sector"),
                        dbc.Input(id='auto_sector', type="text", disabled=True)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("School Subclassification"),
                        dbc.Input(id='auto_subclassification', type="text", disabled=True)
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("School Type"),
                        dbc.Input(id='auto_type', type="text", disabled=True)
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Modified COC"),
                        dbc.Input(id='auto_coc', type="text", disabled=True)
                    ], width=6)
                ])
            ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '0.5rem'})
        ], className="mb-5"),
        dbc.Row([
            dbc.Col([
                dbc.Label("School Year"),
                dcc.Dropdown(id='input_school_year', options=school_year_options, placeholder="Select School Year")
            ], width=6),
            dbc.Col([
                dbc.Label("Grade Level"),
                dcc.Dropdown(id='input_grade', options=grade_options, placeholder="Select Grade")
            ], width=6)
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
                    labelStyle={'margin-right': '20px'},
                    inline=True
                )
            ], width=6),
            dbc.Col([
                dbc.Label("Enrollment Count"),
                dcc.Input(id='input_enrollment', type='number', placeholder="Enter Enrollment Count", className="form-control")
            ], width=6)
        ], className="mb-5"),

        html.Div(
            dbc.Button("Submit", id="submit_button", color="primary"),
            className="text-center mb-5",
            
        ),
        html.Div(id="submission_feedback", className="text-success mt-3"),
        dcc.Store(id='refresh_school_year_trigger', data='initial-load'),
        dbc.Modal([
            dbc.ModalHeader("Missing Fields"),
            dbc.ModalBody([
                html.Div(id="missing-fields-message"),
            ]),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-missing-fields-modal", className="ms-auto", color="secondary")
            ])
        ], id="missing-fields-modal", is_open=False),
        # Enrollment Table
        html.Hr(),
        html.H4("View Enrollment Table by School Year", className="mt-4 mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Select School Year to View Table"),
                    dcc.Dropdown(
                        id='table_school_year',
                        placeholder="Select School Year",
                        value="2023-2024",
                        options=[{'label': y, 'value': y} for y in available_years],
                    )
            ])
        ], className="mb-3"),
        dbc.Modal([
            dbc.ModalHeader("Confirm Submission"),
            dbc.ModalBody([
                html.Div(id="confirm-message"),
                dbc.Checkbox(
                    id="confirm-checkbox",
                    label="Yes, I confirm this data is correct.",
                    className="mt-3"
                )
            ]),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="close-confirm-modal", className="me-2", color="secondary"),
                dbc.Button("Finalize", id="finalize-submit", color="success", disabled=True)
            ])
        ], id="confirm-modal", is_open=False),

        dash_table.DataTable(
            id='enrollment_table',
            columns=[],
            data=[],
            page_size=10,
            sort_action='native',
            filter_action='native',
            style_table={'overflowX': 'auto'}
        )
    ], fluid=True)
