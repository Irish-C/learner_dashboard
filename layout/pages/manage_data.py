
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from app_data import get_available_school_years
available_years = get_available_school_years()

def manage_data_content(region_options, grade_options, school_year_options):
    return dbc.Container([
        html.H1("Manage Data Page", className="page-title mb-4"),
        html.H3("Add New Enrollment Record", className="mb-4"),

        html.H4("Enrollment Information", className="mb-3"),
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
            className="text-center mb-5"
        ),

        html.Div(id="submission_feedback", className="text-success mt-3"),
        dcc.Store(id='refresh_school_year_trigger'),
        html.Hr(),
        html.H4("View Enrollment Table by School Year", className="mt-4 mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Select School Year to View Table"),
                dcc.Dropdown(
                    id='table_school_year',
                    options=[{'label': y, 'value': y} for y in available_years],
                    placeholder="Select School Year"
                )
            ])
        ], className="mb-3"),

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
