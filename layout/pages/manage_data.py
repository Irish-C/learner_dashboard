import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from app_data import get_available_school_years

available_years = get_available_school_years()
def manage_data_content(region_options, grade_options, school_year_options):
        # ➡️ Add this inside the function
    def extend_grade_options_with_strands(original_grade_options):
        # map friendly name → actual dataset base
        shs_map = {
            'ABM': 'ACAD - ABM',
            'HUMSS': 'ACAD - HUMSS',
            'STEM': 'ACAD STEM',
            'GAS': 'ACAD GAS',
            'PBM': 'ACAD PBM',
            'TVL': 'TVL',
            'SPORTS': 'SPORTS',
            'ARTS & DESIGN': 'ARTS'
        }
        new_options = []
        for option in original_grade_options:
            value = option['value']
            if value in ['G11', 'G12']:
                for strand, dataset_str in shs_map.items():
                    new_options.append({
                        'label': f"Grade {value[1:]} - {strand}",
                        'value': f"{value} {dataset_str}"  # this matches your column format
                    })
            else:
                new_options.append(option)
        return new_options

    # ➡️ Call the extender immediately
    grade_options = extend_grade_options_with_strands(grade_options)
    return dbc.Container([
        html.H1("Manage Data", className="page-title mb-4"),
        html.H3("Add New Enrollment Record", className="mb-4"),
        
        # Enclose Inputs from Upload CSV Button to Submit Button in a Card
        dbc.Card([
            dbc.CardHeader("Enrollment Record Details", className="fw-bold"),
            dbc.CardBody([
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

                        # Upload Area
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

                # Region and Division selection
                html.H6("Manual Input", className="mb-2"),
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

                # School Name selection
                dbc.Row([
                    dbc.Col([
                        dbc.Label("School Name"),
                        dcc.Dropdown(id='input_school_name', options=[], placeholder="Search School", searchable=True, disabled=True)
                    ])
                ], className="mb-4"),

                # Auto-Filled School Information Section
                dbc.Card([
                    dbc.CardHeader("Auto-Filled School Information", className="fw-bold", style={"textAlign": "center"}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("BEIS School ID", style={"textAlign": "center"}),
                                dbc.Input(id='beis_school_id_display', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Barangay", style={"textAlign": "center"}),
                                dbc.Input(id='auto_barangay', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6)
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Sector", style={"textAlign": "center"}),
                                dbc.Input(id='auto_sector', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6),
                            dbc.Col([
                                dbc.Label("School Subclassification", style={"textAlign": "center"}),
                                dbc.Input(id='auto_subclassification', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6)
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("School Type", style={"textAlign": "center"}),
                                dbc.Input(id='auto_type', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Modified COC", style={"textAlign": "center"}),
                                dbc.Input(id='auto_coc', type="text", disabled=True, style={"textAlign": "center"})
                            ], width=6)
                        ])
                    ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '0.5rem'})
                    ], className="mb-5", style={
                        "boxShadow": "none", 
                        "transition": "none", 
                        "transform": "none", 
                        "position": "relative"
                    }),  # Disable hover pop-up animation

                # School Year and Grade Level selection
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

                # Male and Female Enrollment Counts
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Male Enrollment Count", style={"textAlign": "center"}),
                        dcc.Input(
                            id='input_enrollment_male', 
                            type='number', 
                            placeholder="Enter Male Enrollment Count", 
                            className="form-control", 
                            style={'textAlign': 'center'}
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Female Enrollment Count", style={"textAlign": "center"}),
                        dcc.Input(
                            id='input_enrollment_female', 
                            type='number', 
                            placeholder="Enter Female Enrollment Count", 
                            className="form-control", 
                            style={'textAlign': 'center'}
                        )
                    ], width=6)
                ], className="mb-5"),
                # Submit Button
                html.Div(
                    dbc.Button("Submit", id="submit_button", color="primary"),
                    className="text-center mb-5",
                ),
                html.Div(id="submission_feedback", className="text-success mt-3"),
            ])
        ], className="mb-5", style={
            "boxShadow": "none", 
            "transition": "none", 
            "transform": "none", 
            "position": "relative"
        }),  # Disable hover pop-up animation

        dcc.Store(id='refresh_school_year_trigger', data='initial-load'),

        # Missing Fields Modal
        dbc.Modal([
            dbc.ModalHeader("Missing Fields"),
            dbc.ModalBody([html.Div(id="missing-fields-message")]),
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