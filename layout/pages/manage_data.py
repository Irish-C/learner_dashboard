import dash_bootstrap_components as dbc
from dash import html, dcc

layout = dbc.Container([
    html.H1("Manage Data Page", className="page-title"),
    html.H3("Add New Enrollment Record", className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Region"),
            dcc.Dropdown(id='input_region', placeholder="Select Region")
        ]),
        dbc.Col([
            dbc.Label("Division"),
            dcc.Dropdown(id='input_division', placeholder="Select Division")
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("School Name"),
            dcc.Dropdown(id='input_school_name', placeholder="Select School")
        ]),
        dbc.Col([
            dbc.Label("Barangay"),
            dcc.Dropdown(id='input_barangay', placeholder="Select Barangay")
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("School Year"),
            dcc.Input(id='input_school_year', type='text', placeholder="e.g., 2024-2025", className="form-control")
        ]),
        dbc.Col([
            dbc.Label("Grade Level"),
            dcc.Dropdown(
                id='input_grade',
                options=[{'label': f"{g}", 'value': f"G{g}" if g != 'K' else 'K'} for g in ['K'] + list(range(1, 13))],
                placeholder="Select Grade"
            )
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Gender"),
            dcc.Dropdown(id='input_gender', options=[
                {'label': 'Male', 'value': 'Male'},
                {'label': 'Female', 'value': 'Female'},
                {'label': 'Both', 'value': 'Both'}
            ], placeholder="Select Gender")
        ]),
        dbc.Col([
            dbc.Label("Enrollment Count"),
            dcc.Input(id='input_enrollment', type='number', placeholder="Enter Enrollment Count", className="form-control")
        ])
    ], className="mb-4"),

    dbc.Button("Submit", id="submit_button", color="primary", className="mb-3"),
    html.Div(id="submission_feedback", className="text-success")
])

    
print("Manage Data loaded...")        
