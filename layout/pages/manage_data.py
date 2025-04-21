import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from app_data import region_options,division_options,barangay_options,school_options,gender_options,grade_options
form_layout = dbc.Container([
    html.H3("Add New Enrollment Entry", className="mb-3"),
    dbc.Row([
        dbc.Col([dbc.Label("School Year"), dcc.Input(id="input-year", type="text", placeholder="e.g., 2023-2024", className="form-control")], md=4),
        dbc.Col([dbc.Label("Region"), dcc.Dropdown(id="input-region", options=region_options, placeholder="Select Region")], md=4),
        dbc.Col([dbc.Label("Division"), dcc.Dropdown(id="input-division", options=division_options, placeholder="Select Division")], md=4),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([dbc.Label("Barangay"), dcc.Dropdown(id="input-barangay", options=barangay_options, placeholder="Select Barangay")], md=6),
        dbc.Col([dbc.Label("School"), dcc.Dropdown(id="input-school", options=school_options, placeholder="Select School")], md=6),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([dbc.Label("Grade Level"), dcc.Dropdown(id="input-grade", options=grade_options, placeholder="Select Grade")], md=6),
        dbc.Col([dbc.Label("Gender"), dcc.Dropdown(id="input-gender", options=gender_options, placeholder="Select Gender")], md=6),
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([dbc.Label("Enrollment Count"), dcc.Input(id="input-enrollment", type="number", min=0, className="form-control", placeholder="e.g., 123")])
    ], className="mb-3"),
    dbc.Row([
        dbc.Col([dbc.Button("Submit Entry", id="submit-entry", color="primary", className="me-2")])
    ])
], fluid=True)


def manage_data_content(region_options, division_options, school_options, barangay_options):
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
                dcc.Dropdown(id='input_division', options=division_options, placeholder="Select Division")
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("School Name"),
                dcc.Dropdown(id='input_school_name', options=school_options, placeholder="Select School")
            ]),
            dbc.Col([
                dbc.Label("Barangay"),
                dcc.Dropdown(id='input_barangay', options=barangay_options, placeholder="Select Barangay")
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("School Year"),
                dcc.Input(id='input_school_year', type='text', placeholder="e.g., 2024-2025", className="form-control")
            ]),
            dbc.Col([
                dbc.Label("Grade Level"),
                dcc.Dropdown(id='input_grade', options=[{'label': f'Grade {i}', 'value': f'G{i}'} for i in range(1, 13)],
                             placeholder="Select Grade")
            ]),
            dbc.Col([
                dbc.Label("Gender"),
                dcc.Dropdown(id='input_gender', options=[
                    {'label': 'Male', 'value': 'Male'},
                    {'label': 'Female', 'value': 'Female'}
                ], placeholder="Select Gender")
            ]),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Enrollment Count"),
                dcc.Input(id='input_enrollment', type='number', placeholder="Enter Enrollment Count", className="form-control")
            ]),
        ], className="mb-3"),
        dbc.Button("Submit", id="submit_data_btn", color="primary", className="mt-3"),
        html.Div(id='submission_status', className="mt-3")
    ])
    
print("Manage Data loaded...")        
