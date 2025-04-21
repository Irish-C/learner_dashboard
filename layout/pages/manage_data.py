import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

schools_df = pd.read_csv("schools.csv")

region_options = [{'label': r, 'value': r} for r in sorted(schools_df['Region'].dropna().unique())]
division_options = [{'label': d, 'value': d} for d in sorted(schools_df['Division'].dropna().unique())]
barangay_options = [{'label': b, 'value': b} for b in sorted(schools_df['Barangay'].dropna().unique())]
school_options = [{'label': name, 'value': sid} for sid, name in zip(schools_df['BEIS School ID'], schools_df['School Name'])]

grade_options = [{'label': f'Grade {g}', 'value': f'G{g}'} for g in range(1, 13)]
grade_options.insert(0, {'label': 'Kinder', 'value': 'K'})
gender_options = [{'label': 'Male', 'value': 'Male'}, {'label': 'Female', 'value': 'Female'}]

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


def manage_data_content():
    return html.Div(children=[
        html.H1("Manage Data Page", className="page-title"),
        html.Div("Content for Manage Data Page goes here.", style={"fontSize": "1.2rem"})
    ])

print("Manage Data loaded...")