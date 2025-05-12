import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import json
import os, io, base64
import hashlib
from datetime import datetime
import time

from layout.pages.settings import settings_content
from layout.sidebar import create_sidebar
from layout.header import create_header
from layout.page_router import get_content_style, create_content
from app_data import (
    get_school_metadata,
    load_schools,
    load_data_for_year,
    build_combined_shs_track_df,
    get_available_school_years
    )

# Path to user info CSV file
USER_CSV_PATH = "data_files/user-info.csv"

# Function to hash a password
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Load user data from CSV
if os.path.exists(USER_CSV_PATH):
    user_df = pd.read_csv(USER_CSV_PATH)
else:
    user_df = pd.DataFrame(columns=['First_Name', 'Last_Name', 'Email', 'Password'])  # Initialize an empty DataFrame
    raise FileNotFoundError(f"{USER_CSV_PATH} does not exist. An empty user DataFrame has been created.")

# Hash passwords in the dataframe
user_df['Password'] = user_df['Password'].apply(hash_password)

# Convert to list of dictionaries for use in login
USER_DATA = user_df.to_dict(orient='records')

# Mapping of numeric values to page names
PAGE_CONSTANTS = {
    1: 'dashboard',
    2: 'manage_data',
    3: 'help',
    4: 'settings'
}

#log in page layout
login_page = dbc.Container([
    dcc.Store(id="login-state", storage_type="session", data={"logged_in": False}),
    dbc.Row([
        dbc.Col([
            html.H3("Login", className="text-center mb-3"),
            dbc.Input(id="input-firstname", placeholder="First Name", type="text", className="w-100"),
            dbc.Input(id="input-lastname", placeholder="Last Name", type="text", className="w-100"),
            html.Div(id="login-message", className="text-center", style={"color": "red", "marginTop": "10px", "fontWeight": "bold", "fontSize": "16px"})
        ], width=4)
    ], justify="center", style={"paddingTop": "15%"})
], fluid=True)

# Upload Format
correct_columns = [
    "School Year", "BEIS School ID", "K Male", "K Female", "G1 Male", "G1 Female",
    "G2 Male", "G2 Female", "G3 Male", "G3 Female", "G4 Male", "G4 Female",
    "G5 Male", "G5 Female", "G6 Male", "G6 Female", "Elem NG Male", "Elem NG Female",
    "G7 Male", "G7 Female", "G8 Male", "G8 Female", "G9 Male", "G9 Female",
    "G10 Male", "G10 Female", "JHS NG Male", "JHS NG Female",
    "G11 ACAD - ABM Male", "G11 ACAD - ABM Female", "G11 ACAD - HUMSS Male", "G11 ACAD - HUMSS Female",
    "G11 ACAD STEM Male", "G11 ACAD STEM Female", "G11 ACAD GAS Male", "G11 ACAD GAS Female",
    "G11 ACAD PBM Male", "G11 ACAD PBM Female", "G11 TVL Male", "G11 TVL Female",
    "G11 SPORTS Male", "G11 SPORTS Female", "G11 ARTS Male", "G11 ARTS Female",
    "G12 ACAD - ABM Male", "G12 ACAD - ABM Female", "G12 ACAD - HUMSS Male", "G12 ACAD - HUMSS Female",
    "G12 ACAD STEM Male", "G12 ACAD STEM Female", "G12 ACAD GAS Male", "G12 ACAD GAS Female",
    "G12 ACAD PBM Male", "G12 ACAD PBM Female", "G12 TVL Male", "G12 TVL Female",
    "G12 SPORTS Male", "G12 SPORTS Female", "G12 ARTS Male", "G12 ARTS Female"
]

# Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
    assets_folder='assets',
    suppress_callback_exceptions=True,
    title="Learner Information System"
)


# Load index template from the HTML file
with open('assets/index_template.html', 'r') as file:
    app.index_string = file.read()

# Generate school year options
current_year = datetime.now().year
school_year_options = [{'label': f"{y}-{y+1}", 'value': f"{y}-{y+1}"} for y in range(current_year - 20, current_year + 5)]
# Default year to load initially
default_school_year = "2023-2024"
data, grade_columns, grade_options, region_options = load_data_for_year(default_school_year)
combined_shs_track_df = build_combined_shs_track_df(data)

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id="login-state", storage_type="session", data={"logged_in": False}),
    dcc.Store(id="stored_data", data=data.to_dict("records")),
    dcc.Store(id="stored_grades", data=grade_columns),
    dcc.Store(id="stored_grade_options", data=grade_options),
    dcc.Store(id="stored_region_options", data=region_options),
    dcc.Store(id="stored_school_year", data=default_school_year),
    dcc.Store(id='trigger_enrollment_table_reload'),
    dcc.Store(id='refresh_school_year_trigger', data='initial-load'),
    html.Div(id="page-content")
])

# Callback for login
@app.callback(
    Output("login-state", "data"),
    Output("login-message", "children"),
    Input("login-button", "n_clicks"),
    State("input-firstname", "value"),
    State("input-lastname", "value"),
    State("input-email", "value"),
    State("input-password", "value"),
    prevent_initial_call=True
)
def verify_login(n_clicks, first_name, last_name, email, password):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    if not all([first_name, last_name, email, password]):
        return dash.no_update, "⚠️ Please fill in all fields."

    pw_hash = hash_password(password)
    for user in USER_DATA:
        if (user["First_Name"].lower() == first_name.lower() and
            user["Last_Name"].lower() == last_name.lower() and
            user["Email"].lower() == email.lower() and
            user["Password"] == pw_hash):
            return {"logged_in": True, "user": f"{first_name} {last_name}","avatar": user["avatar"]
                    },""

    return dash.no_update, "❌ Invalid credentials. Please try again."


@app.callback(
    Output("sidebar-container", "children"),
    Output("content", "children"),
    Output("content", "style"),
    Output("sidebar-toggle-state", "data"),
    Output("current-page", "data"),
    Input("sidebar-toggle", "n_clicks"),
    Input("btn-1", "n_clicks"),
    Input("btn-2", "n_clicks"),
    Input("btn-3", "n_clicks"),
    Input("btn-4", "n_clicks"),
    State("sidebar-toggle-state", "data"),
    State("current-page", "data"),
    State("login-state", "data")
)
def handle_interaction(toggle_clicks, b1, b2, b3, b4, is_collapsed, current_page, login_state):
    ctx = callback_context

    new_collapsed = is_collapsed
    new_page = current_page

    if ctx.triggered:
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "sidebar-toggle":
            new_collapsed = not is_collapsed

        button_to_page = {
            "btn-1": PAGE_CONSTANTS[1],
            "btn-2": PAGE_CONSTANTS[2],
            "btn-3": PAGE_CONSTANTS[3],
            "btn-4": PAGE_CONSTANTS[4],
        }
        if triggered_id in button_to_page:
            new_page = button_to_page[triggered_id]

    sidebar = create_sidebar(is_collapsed=new_collapsed, current_page=new_page)

    if new_page == "settings":
        current_user = login_state["user"] if login_state and "user" in login_state else ""
        content = settings_content(current_user)
    else:
        content = create_content(new_page, data, grade_options, region_options, school_year_options)

    content_style = get_content_style(new_collapsed)

    return sidebar, content, content_style, new_collapsed, new_page

# Call back for same profile pic
@app.callback(
    Output("user-avatar", "src"),
    Output("user-name", "children"),
    Input("login-state", "data")
)
def update_user_profile(login_data):
    if login_data and login_data.get("logged_in"):
        avatar_filename = login_data.get("avatar", "")
        avatar_path = (
            f"/assets/avatars/{avatar_filename}"
            if pd.notna(avatar_filename) and os.path.isfile(f"assets/avatars/{avatar_filename}")
            else "/assets/avatars/default.jpg"
        )
        username = login_data.get("username", login_data.get("user", "User"))
        return avatar_path, username

    return "/assets/avatars/default.jpg", "Guest"

# Call back for login to dashboard
@app.callback(
    Output("page-content", "children"),
    Input("login-state", "data")
)
def load_protected_page(login_data):
    input_style = {
        'width': '100%',
        'paddingRight': '40px',
        'padding': '10px',
        'fontSize': '16px',
        'borderRadius': '5px',
        'border': '1px solid #5A5A5A'
    }

    if login_data["logged_in"]:
        first_name = login_data.get("user").split()[0]
        print(f"Stored first name: {first_name}")  # Debug print to ensure the first name is stored
        return html.Div(
    className="body-style",
    children=[
        # Welcome Modal
        dbc.Modal(
            id="welcome-modal",
            is_open=True,
            size="lg",
            centered=True,
            children=[
                dbc.ModalHeader(
                    html.H2([
                        "W E L C O M E    ",
                        html.Span(first_name.upper(), style={"color": "gold", "fontWeight": "bold","letterSpacing": "5px","fontFamily": "Roboto, sans-serif"}),
                        "!",
                    ]),
                    close_button=True,
                    style={"backgroundColor": "#0d3c74", "color": "white", "borderRadius": "10px 10px 0 0"}
                ), 
                dbc.ModalBody([
                    html.P([
                        "This is ",
                        html.Span("LIS", style={"color": "#0d3c74","fontweight":"bold","fontFamily": "Roboto, sans-serif","letterSpacing": "2.5px","fontSize": "16px"}),
                        html.Span("tahan", style={"color": "red", "fontWeight": "bold","fontFamily": "Roboto, sans-serif","letterSpacing": "2.5px","fontSize": "16px"}),
                        html.Span(": Organize Today. Empower Tomorrow",style={"color": "#0d3c74","fontSize": "17px", "fontFamily": "Roboto, sans-serif","letterSpacing": "2.5px"})
                    ], style={"fontSize": "18px", "fontFamily": "Roboto, sans-serif","letterSpacing": "2px","marginTop": "10px","fontSize": "16px"}),

                    html.P("A DepEd Learner Information System built just for you.",style={"fontFamily": "Roboto, sans-serif","letterSpacing": "2.5px","fontSize": "16px"}),
                    html.P("Click around, discover features, and make learning seamless!", style={"fontStyle": "italic","fontFamily": "Roboto, sans-serif","marginTop": "30px","letterSpacing": "2.5px", "marginBottom": "0","fontSize": "16px"}),
                    html.Img(src="/assets/icons/LIST.png", style={"height": "45px", "float": "right","marginTop": "-40px","marginBottom": "10px" })
                ], style={"padding": "1.5rem"})
            ],
            style={"borderRadius": "12px", "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",}
        ),

        dcc.Store(id='sidebar-toggle-state', data=False),
        dcc.Store(id='current-page', data="dashboard"),
        dcc.Store(id='user-first-name', data=first_name),
        create_header(),
        html.Div(
            className="app-container",
            children=[
                html.Div(id="sidebar-container", children=[
                    create_sidebar(is_collapsed=False, current_page="dashboard")
                ]),
                html.Div(id="content", style=get_content_style(False), children=create_content(
                    "dashboard", data, grade_options, region_options, school_year_options
                ))
            ]
        )
    ]
)

    return html.Div(
    style={
        "height": "100vh",
        "width": "100%",
        "backgroundImage": 'url("/assets/icons/class.png")',
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "display": "flex",
        "justifyContent": "flex-end",
        "alignItems": "stretch"
    },
    children=[
        html.Div([
            # Logo and Title - CENTERED
            html.Div([
                html.Img(src="/assets/icons/LIST.png", style={"height": "140px", "marginBottom": "10px"}),
                html.H4("LEARNER INFORMATION SYSTEM", style={
                    "fontWeight": "bold",
                    "letterSpacing": "2px",
                    "fontSize": "16px",
                    "letterSpacing": "0.30em",
                    "fontFamily": "Roboto, sans-serif",
                    "marginTop": "20px",
                    "marginBottom": "20px"
                })
            ], style={"textAlign": "center",
                      "marginBottom": "20px"}),

            # Input Fields
            dcc.Store(id="user-first-name"),
            dbc.Input(id="input-firstname", placeholder="F I R S T   N A M E", type="text", className="mb-3", style={"fontFamily": "Roboto, sans-serif",
            "boxShadow": "4px 4px 8px rgba(30,144,255,0.4)",
            "border": "none",
            "borderRadius": "10px",
            "fontSize": "15px",
            "lineHeight": "2.5",
            "paddingLeft": "2rem"}),
            
            dbc.Input(id="input-lastname", placeholder="L A S T   N A M E", type="text", className="mb-3", style={"fontFamily": "Roboto, sans-serif",
            "boxShadow": "4px 4px 8px rgba(30,144,255,0.4)",
            "border": "none",
            "borderRadius": "10px",
            "fontSize": "15px",
            "lineHeight": "2.5",
            "paddingLeft": "2rem"}),
            dbc.Input(id="input-email", placeholder="E M A I L   A D D R E S S", type="email", className="mb-3", style={"fontFamily": "Roboto, sans-serif",
            "boxShadow": "4px 4px 8px rgba(30,144,255,0.4)",
            "border": "none",
            "borderRadius": "10px",
            "fontSize": "15px",
            "lineHeight": "2.5",
            "paddingLeft": "2rem"}),
            html.Div([dbc.Input(id="input-password", type="password", placeholder="P A S S W O R D", className="w-100", style={
                "fontFamily": "Roboto, sans-serif",
                "boxShadow": "4px 4px 8px rgba(30,144,255,0.4)",
                "border": "none",
                "borderRadius": "10px",
                "fontSize": "15px",
                "lineHeight": "2.5",
                "paddingLeft": "2rem"
            }),
                html.I(
                    id="toggle-password-visibility",
                    className="fas fa-eye",  # starts as eye
                    n_clicks=0,
                    style={
                        "position": "absolute",
                        "right": "20px",
                        "top": "50%",
                        "transform": "translateY(-50%)",
                        "cursor": "pointer",
                        "color": "#5A5A5A"
                    }
                )
            ], style={"position": "relative", "marginBottom": "1rem"}),
            # Sign-In Button
            dbc.Button("SIGN-IN", id="login-button", color="danger", className="w-100 mb-3", style={
                "fontWeight": "bold",
                "letterSpacing": "2px",
                "backgroundColor": "#DE082C",
                "border": "none"
            }),

            # Message Display
            html.Div(id="login-message", className="text-left", style={
                "color": "red",
                "fontWeight": "bold",
                "fontSize": "16px"
            }),

            # Footer Text
            html.Div("© 2025 LISTahan. All Right Reserved.", className="text-left mt-7", style={
                "fontSize": "12px", "color": "#888", "textAlign": "center", "marginTop": "40px"
            })
        ], style={
            "width": "100%",
            "maxWidth": "500px",  # ← Adjust width here
            "height": "100vh",
            "padding": "40px",
            "paddingTop": "60px",
            "backgroundColor": "rgba(255, 255, 255, 0.85)",
            "borderLeft": "5px solid #DE082C",
            "boxShadow": "0 0 15px rgba(0, 0, 0, 0.25)",
            "borderLeft": "none",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "flex-start",
            "backgroundImage": "url('/assets/your-bg.jpg')",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
            "backdropFilter": "blur(8px)",
            "WebkitBackdropFilter": "blur(8px)", 
            "width": "100%",
            "minHeight": "100vh",
            "backgroundColor": "rgba(255,255,255,0.75)",   
        })
    ]
)
@app.callback(
    Output("welcome-modal", "is_open"),
    Output("welcome-modal-body", "children"),
    Input("login-state", "data"),
    Input("close-welcome-modal", "n_clicks"),
    State("welcome-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_welcome_modal(login_data, close_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger == "login-state" and login_data.get("logged_in"):
        return True, f"Welcome, {login_data.get('user', 'User')}! 🎉"
    elif trigger == "close-welcome-modal":
        return False, dash.no_update

    return is_open, dash.no_update


@app.callback(
    Output('input-password', 'type'),
    Output('toggle-password-visibility', 'className'),
    Input('toggle-password-visibility', 'n_clicks'),
    State('input-password', 'type'),
    prevent_initial_call=True
)
def toggle_password_visibility(n_clicks, current_type):
    if current_type == 'password':
        return 'text', 'fas fa-eye-slash'
    return 'password', 'fas fa-eye'


@app.callback(
    Output('user-first-name', 'data'),  # Store the first name in `data`
    Input('login-button', 'n_clicks'),
    State('input-firstname', 'value'),
    prevent_initial_call=True
)

def store_user_first_name(n_clicks, firstname):
    if n_clicks > 0:  # Check if the button has been clicked
        print(f"Storing first name: {firstname}")
        return {"firstname": firstname}
    return dash.no_update

def toggle_password_visibility(n_clicks, current_type):
    if current_type == 'password':
        return 'text', 'fas fa-eye-slash'
    return 'password', 'fas fa-eye'

# Dashboard Page

PLOT_TITLE=dict(        # Create consistent title style for all plots
    size=22,
    color="#0a4485",
    family="Roboto, sans-serif",
) 

@app.callback(
    Output('school_year_filter', 'options'),
    Output('school_year_filter', 'value'),
    Input('upload-data', 'contents'),
    Input('input_school_year', 'value'),  # Input from manual entry
    prevent_initial_call=False
)
def update_school_year_dropdown(upload_contents, manual_year):
    # Get the updated school years
    school_years = get_available_school_years()  # This could be updated when file is uploaded or a new year is manually entered

    # Sort the years
    school_years.sort()

    # Set default value
    default_year = manual_year if manual_year in school_years else school_years[-1]  # Use the manually entered year if valid

    # Create the options for the dropdown
    options = [{'label': year, 'value': year} for year in school_years]

    return options, default_year




@app.callback(
    [Output('gender_pie_chart', 'figure'),
     Output('enrollment_vs_schools_chart', 'figure'),
     Output('kpi_card_row', 'children'),
     Output('most_enrolled_division_card', 'children')],
    [Input('region_filter', 'value'),
     Input('grade_filter', 'value'),
     Input('school_year_filter', 'value'),
     Input('gender_filter', 'value')]
)

def update_charts(selected_regions, selected_grades, selected_school_year, selected_gender):
    if not selected_school_year:
        raise dash.exceptions.PreventUpdate
    try:
        data, grade_columns, _, _ = load_data_for_year(selected_school_year)
    except FileNotFoundError:
        raise dash.exceptions.PreventUpdate
     
    filtered_data = data.copy()

    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    selected_cols_male = []
    selected_cols_female = []

    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]

    # Apply gender filtering to the DataFrame
    filtered_data = data.copy()
    if selected_gender == 'Male':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

    # Pie Chart
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]
    total_male = filtered_data[selected_cols_male].sum().sum()
    total_female = filtered_data[selected_cols_female].sum().sum()
    pie_chart = px.pie(
        names=['Male', 'Female'],
        values=[total_male, total_female],
        title='Gender Distribution',
        hole=0.6,
        color_discrete_sequence=['#0a4485', '#DE082C']
    )

    pie_chart.update_traces(
        textinfo='percent',
        hovertemplate='%{label} students: %{value:,}<extra></extra>')

    pie_chart.update_layout(
        margin=dict(t=50, b=0, l=0, r=0),
        title_font=PLOT_TITLE,
        height=296,  # or adjust for your visual preference
        showlegend=True  # set to False if pie labels suffice
    )

    # Filter by selected regions
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]
    
    if selected_gender == 'Male':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

    # Group by Division and Region
    agg_division = filtered_data.groupby(['Division', 'Region']).agg({
        'BEIS School ID': 'count',
        'Selected Grades Total': 'sum'
    }).rename(columns={'BEIS School ID': 'Number of Schools'}).reset_index()

    # Sort and select top 15 divisions
    agg_division = agg_division.sort_values(by='Selected Grades Total', ascending=False).head(15)

    # Create the figure
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])

    fig_combo.add_trace(go.Bar(
        x=agg_division['Division'],
        y=agg_division['Selected Grades Total'],
        name='Total Enrollment',
        marker_color='#0a4485',  # Blue
        hovertemplate='<b>%{x}</b><br>Students: %{y:,}<extra></extra>',
    ), secondary_y=False)

    fig_combo.add_trace(go.Scatter(
        x=agg_division['Division'],
        y=agg_division['Number of Schools'],
        name='Number of Schools',
        line=dict(color='#DE082C'),  # Red
        hovertemplate='<b>%{x}</b><br>Schools: %{y:,}<extra></extra>',
        mode='lines+markers'
    ), secondary_y=True)

    fig_combo.update_layout(
        title='Top 15 Divisions: Total Enrollment and Number of Schools',
        title_font=PLOT_TITLE,
        xaxis_title='Division',
        yaxis_title='Total Enrollment'
    )

    # KPI Cards Layout
    # Aggregate stats
    total_students = int(filtered_data['Selected Grades Total'].sum())
    total_schools = filtered_data['BEIS School ID'].nunique()
    region_total = filtered_data.groupby('Region')['Selected Grades Total'].sum().max()

    # 🔓 Use full dataset to get the true most enrolled region (before filtering by selected_regions)
    full_region_data = data.copy()

    # Optional: filter by gender and grades, but NOT by region
    selected_cols = []
    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols += [col for col in full_region_data.columns if col.startswith(grade)]
            else:
                selected_cols += [f"{grade} Male", f"{grade} Female"]
    else:
        selected_cols = grade_columns

    if selected_gender == 'Male':
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols if 'Male' in col]].sum(axis=1)
    elif selected_gender == 'Female':
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols if 'Female' in col]].sum(axis=1)
    else:
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols]].sum(axis=1)

    # 🔍 Calculate most enrolled region regardless of region filter
    region_enrollment = full_region_data.groupby('Region')['Selected Grades Total'].sum()
    most_enrolled_region = region_enrollment.idxmax()
    region_total = region_enrollment.max()

    # Calculate the sector counts and percentages
    sector_counts = data['Sector'].value_counts()
    sector_total_schools = sector_counts.sum()
    sector_percentage = (sector_counts / sector_total_schools) * 100

    # Format percentages for each sector
    public_percentage = sector_percentage.get('Public', 0)
    private_percentage = sector_percentage.get('Private', 0)
    sucs_lucs_percentage = sector_percentage.get('SUCsLUCs', 0) 


    # KPI Cards (now with Sector card inside the 4-col row)
    card_style = {
        "minHeight": "175px",
        "border": "none",
        "borderRadius": "0.625rem",
        "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
        "padding": "10px",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "space-between",
        "transition": "all 0.3s ease",
        "backgroundColor": "white",
        "width": "100%",
        "maxWidth": "100%",
        
        
    }
    text_style = {
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "center",
        "height": "100%",
        "color": "black"
    }

    kpi_cards = dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-user-graduate", style={"fontSize": "30px", "color": "var(--primary-color)", "marginBottom": "10px"}),
                        html.H5("Total Enrolled", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H2(f"{total_students:,}", style={"color": "var(--primary-color)", "margin": "0"})
                    ], style=text_style)
                ]),
                style={**card_style, "borderBottom": "5px solid var(--primary-color)"}
            ),
            xs=12, sm=6, md=6, lg=3,
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-school", style={"fontSize": "30px", "color": "var(--secondary-color)", "marginBottom": "10px"}),
                        html.H5("Total Schools", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H2(f"{total_schools:,}", style={"color": "var(--secondary-color)", "margin": "0"})
                    ], style=text_style)
                ]),
                style={**card_style, "borderBottom": "5px solid var(--secondary-color)"}

            ),
            xs=12, sm=6, md=6, lg=3,
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-map-marked-alt", style={"fontSize": "35px", "color": "var(--success-color)", "marginBottom": "10px"}),
                        html.H5(f"Most Enrolled Region as of {selected_school_year}", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H3(f"{most_enrolled_region}: {region_total/1000:.2f}k", style={"color": "var(--success-color)", "margin": "0", "fontSize": "24px"})
                    ], style=text_style)
                ]),
                style={**card_style, "borderBottom": "5px solid var(--success-color)"}
            ),
            xs=12, sm=6, md=6, lg=3,
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-chalkboard-teacher", style={
                        "fontSize": "35px", 
                        "color": "var(--warning-color)", 
                        "marginBottom": "10px"
                    }),

                    html.H5("School Sector Ratio", style={
                        "color": "var(--gray-color)", 
                        "margin": "0", 
                        "fontWeight": "bold"
                    }),

                    html.Div([
                        # One column per category
                        html.Div([
                            html.H3(f"{public_percentage:.2f}%", style={"margin": "0", "fontSize": "20px", "color": "var(--warning-color)"}),
                            html.H6("Public", style={"margin": "0", "fontSize": "14px", "color": "var(--gray-color)"})
                        ], style={"textAlign": "center", "flex": 1}),

                        html.Div([
                            html.H3(f"{private_percentage:.2f}%", style={"margin": "0", "fontSize": "20px", "color": "var(--warning-color)"}),
                            html.H6("Private", style={"margin": "0", "fontSize": "14px", "color": "var(--gray-color)"})
                        ], style={"textAlign": "center", "flex": 1}),

                        html.Div([
                            html.H3(f"{sucs_lucs_percentage:.2f}%", style={"margin": "0", "fontSize": "20px", "color": "var(--warning-color)"}),
                            html.H6("SUCs/LUCs", style={"margin": "0", "fontSize": "14px", "color": "var(--gray-color)"})
                        ], style={"textAlign": "center", "flex": 1}),
                    ], style={
                        "display": "flex",
                        "width": "100%",
                        "gap": "10px"
                    })
                ], style=text_style)

                ]),
                style={**card_style, "borderBottom": "5px solid var(--warning-color)"}
            ),
            xs=12, sm=6, md=6, lg=3,
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        )
    ], justify="center", align="start")
    
    

    # Standalone Most Enrolled Division Card
    most_enrolled_division_text = filtered_data.groupby('Division')['Selected Grades Total'].sum().idxmax()
    most_enrolled_division_card = html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-users-cog", style={"fontSize": "30px", "color": "#0a4485", "marginBottom": "0.5rem"}),
                    html.H5("Most Enrolled Division", style={"color": "var(--gray-color)", "textAlign": "center", "margin": "0", "lineHeight": "1.2"}),
                    html.H2(f"{most_enrolled_division_text}", style={"color": "var(--pr-color)", "textAlign": "center", "margin": "0"})
                ])
            ]),
            style={**card_style, "width": "100%"}
        )
    ])

    return pie_chart, fig_combo, kpi_cards, most_enrolled_division_card

@app.callback(
    Output('school_search', 'options'),
    Input('school_search', 'search_value'),
    State('school_search', 'value')
)
def update_school_options(search_value, current_value):
    options = []

    # Convert BEIS IDs to string for safety
    data['BEIS School ID'] = data['BEIS School ID'].astype(str)

    if not search_value:
        sample = data[['BEIS School ID', 'School Name']].dropna().head(10)
    else:
        sample = data[
            data['School Name'].str.contains(search_value, case=False, na=False) |
            data['BEIS School ID'].astype(str).str.contains(search_value)
        ].head(20)

    options = [
        {'label': f"{row['BEIS School ID']} - {row['School Name']}", 'value': row['BEIS School ID']}
        for _, row in sample.iterrows()
    ]

    if current_value and all(opt['value'] != current_value for opt in options):
        match = data[data['BEIS School ID'] == current_value]
        if not match.empty:
            row = match.iloc[0]
            top_option = {'label': f"{row['BEIS School ID']} - {row['School Name']}", 'value': row['BEIS School ID']}
            options.insert(0, top_option)


    return options


@app.callback(
    Output('school_modal', 'is_open'),
    Output('modal_school_name', 'children'),
    Output('modal_school_body', 'children'),
    Input('school_search', 'value'),
    Input('modal_close_btn', 'n_clicks'),
    State('school_modal', 'is_open')
)
def toggle_modal(school_id, close_click, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, "", ""

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'modal_close_btn':
        return False, "", ""

    if school_id:
        # Convert both to string for consistent comparison
        school_id_str = str(school_id)
        data['BEIS School ID'] = data['BEIS School ID'].astype(str)

        match = data[data['BEIS School ID'] == school_id_str]

        if not match.empty:
            school = match.iloc[0]
            return True, school['School Name'], html.Div([
                html.P(f"Region: {school.get('Region', 'N/A')}"),
                html.P(f"Division: {school.get('Division', 'N/A')}"),
                html.P(f"Barangay: {school.get('Barangay', 'N/A')}"),
                html.P(f"Total Enrollment: {school.get('Total Enrollment', 'N/A'):,}"),
                html.P(f"Male: {school.get('Total Male', 'N/A'):,}"),
                html.P(f"Female: {school.get('Total Female', 'N/A'):,}")
            ])
        else:
            return False, "", html.Div("⚠ School not found.")
    
    return is_open, "", ""




@app.callback(
    Output('shs_track_bar_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_shs_track_chart(selected_school_year, selected_regions, selected_gender):
    if not selected_school_year:
        raise dash.exceptions.PreventUpdate
    try:
        data, grade_columns, _, _ = load_data_for_year(selected_school_year)
    except FileNotFoundError:
        raise dash.exceptions.PreventUpdate
    df_filtered = combined_shs_track_df.copy()
    # 🧠 Filter by region
    if selected_regions:
        df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]

    # 🧠 Filter by gender
    if selected_gender != 'All':
        df_filtered = df_filtered[df_filtered['Gender'] == selected_gender]

    # ✅ Final protection: prevent plotly from erroring on empty or malformed data
    if df_filtered.empty:
        return go.Figure().update_layout(
            title="No data available for the selected filters",
            xaxis_title='Total Enrollment',
            yaxis_title='Track'
        )

    # 🧾 Group the data
    grouped = df_filtered.groupby(['Track', 'Grade Level'], as_index=False)['Total Enrollment'].sum()

    # 🔐 Defensive: check again if grouped is empty
    if grouped.empty:
        return px.bar(title="No data to display")
    
    # Sort the grouped data by 'Total Enrollment' in ascending order
    grouped = grouped.sort_values(by='Total Enrollment', ascending=True)

    grouped['Display Enrollment'] = grouped['Total Enrollment'] + 30000

    # 📊 Plot the chart safely
    try:
        fig = px.bar(
            grouped,
            x='Display Enrollment',
            y='Track',
            color='Grade Level',
            orientation='h',
            text='Total Enrollment',
            title='Senior High Track Enrollment Overview',
            custom_data=['Grade Level', 'Total Enrollment'],  # ✅ Pass Grade Level for hovertemplate
            color_discrete_map={
                'G12': '#0a4485',   # Blue
                'G11': '#DE082C'    # Red
            }
        )

        fig.update_traces(
            hovertemplate=(
                "Grade Level: %{customdata[0]}<br>" +
                "Track: %{y}<br>" +
                "Enrollment: %{customdata[1]:,} students<extra></extra>"
            ),
            texttemplate='%{customdata[1]:,}',
            textposition='none'
        )

        fig.update_layout(
            title='Senior High Track Enrollment Overview',
            font=dict(size=13),
            height=350,
            xaxis_title='Enrollment',
            yaxis_title='Track',
            title_font=PLOT_TITLE,
        )
        return fig
    except Exception as e:
        print("SHS Chart Rendering Error:", e)
        return px.bar(title="Error rendering SHS Track chart")
    
@app.callback(
    Output('top_schools_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('school_year_filter', 'value')
)
def update_top_schools_chart(selected_regions, selected_grades, selected_gender, selected_school_year):
    if not selected_school_year:
        raise dash.exceptions.PreventUpdate
    try:
        data, grade_columns, _, _ = load_data_for_year(selected_school_year)
    except FileNotFoundError:
        raise dash.exceptions.PreventUpdate
     
    filtered_data = data.copy()
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    selected_cols_male = []
    selected_cols_female = []

    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]

    # Apply gender filtering to the DataFrame
    if selected_gender == 'Male':
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

    # Top 5 schools by enrollment (regardless of sector)
    top_schools_df = (
        filtered_data.groupby(['School Name', 'Sector'], as_index=False)['Filtered Enrollment']
        .sum()
        .sort_values(by='Filtered Enrollment', ascending=False)
        .head(5)
    )

    # Color scheme
    colors = {
        'Public': '#0a4485',
        'Private': 'BFDBFE',
        'SUCsLUCs': '#007BFF'
    }

    # Create sector-based traces
    fig = go.Figure()
    for sector in ['Public', 'Private', 'SUCsLUCs']:
        sector_data = top_schools_df[top_schools_df['Sector'] == sector]
        if not sector_data.empty:
            fig.add_trace(go.Bar(
                y=sector_data['School Name'],
                x=sector_data['Filtered Enrollment'],
                name=sector,
                orientation='h',
                marker=dict(color=colors.get(sector, '#7f8c8d')),
                text=sector_data['Filtered Enrollment'].map('{:,.0f}'.format),
                textposition='inside',
                hovertemplate='<b>%{y}</b><br>Enrollment: %{x:,}<extra></extra>'
            ))

    # Wrap the school names by inserting a line break between the first and second parts
    wrapped_labels = []
    for name in top_schools_df['School Name']:
        parts = name.split(' ', 2)  # Split into the first two parts
        if len(parts) > 2:
            # Join the first two words and the rest with <br> between them
            wrapped_labels.append(parts[0] + ' ' + parts[1] + '<br>' + parts[2])
        else:
            # If there are only two parts, simply join them
            wrapped_labels.append(parts[0] + ' ' + parts[1])

    fig.update_layout(
        title='Top 5 Most Enrolled Schools',
        barmode='stack',
        height=350,
        showlegend=True,
        legend_title_text='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=40, t=60, b=60),
        xaxis=dict(title='Enrollment', gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(
            categoryorder='array',
            categoryarray=top_schools_df['School Name'].tolist()[::-1],
            title='',
            showgrid=False,
            automargin=True,
            ticklabelposition="outside left",
            tickfont=dict(size=13, family="Arial"),
            ticksuffix='  ',
            ticktext=wrapped_labels,  # Use wrapped labels with <br> breaks
            tickmode='array',  # Ensure ticktext is an array
            tickvals=top_schools_df['School Name'].tolist()[::-1]  # Ensure tickvals correspond to wrapped labels
        ),

        font=dict(size=13),
        legend=dict(orientation='h', y=-0.25, x=0.5, xanchor='center'),
        title_font=PLOT_TITLE,
    )
    return fig

@app.callback(
    Output('sned_sector_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_sned_sector_chart(selected_year, selected_regions, selected_gender):
    filtered_df = data.copy()

    if selected_year:
        filtered_df = filtered_df[filtered_df['School Year'] == selected_year]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

    # Select relevant columns for NG enrollment
    male_ng_cols = [col for col in filtered_df.columns if 'NG' in col and 'Male' in col]
    female_ng_cols = [col for col in filtered_df.columns if 'NG' in col and 'Female' in col]

    if selected_gender == 'Male':
        filtered_df['SNed'] = filtered_df[male_ng_cols].sum(axis=1)
        gender_cols = ['SNed']
        stack_name_map = {'SNed': 'Male'}
    elif selected_gender == 'Female':
        filtered_df['SNed'] = filtered_df[female_ng_cols].sum(axis=1)
        gender_cols = ['SNed']
        stack_name_map = {'SNed': 'Female'}
    else:
        filtered_df['SNed_Male'] = filtered_df[male_ng_cols].sum(axis=1)
        filtered_df['SNed_Female'] = filtered_df[female_ng_cols].sum(axis=1)
        gender_cols = ['SNed_Male', 'SNed_Female']
        stack_name_map = {'SNed_Male': 'Male', 'SNed_Female': 'Female'}

    # Group by sector and sum
    grouped = filtered_df.groupby('Sector')[gender_cols].sum().reset_index()
    melted = pd.melt(grouped, id_vars='Sector', var_name='Gender', value_name='Enrollment')
    melted['Gender'] = melted['Gender'].map(stack_name_map)

    fig = px.bar(
        melted,
        x='Sector',
        y='Enrollment',
        color='Gender',
        barmode='stack',
        text='Enrollment',
        title='Special Needs Education Enrollment by<br>School Sector and Gender',
        color_discrete_map={'Male': '#0a4485', 'Female': '#DE082C'}
    )

    fig.update_layout(
        xaxis_title='School Sector',
        yaxis_title='Total Enrollment',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=13),
        height=350,
        legend_title_text='Gender',
        margin=dict(l=20, r=20, t=80, b=40),
        title_font=PLOT_TITLE,
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='inside')
    return fig

@app.callback(
    Output('transition_rate_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_transition_rate_chart(selected_sy, selected_regions, selected_gender):
    try:
        data_curr, _, _, _ = load_data_for_year(selected_sy)
        previous_sy = f"{int(selected_sy.split('-')[0]) - 1}-{int(selected_sy.split('-')[1]) - 1}"
        data_prev, _, _, _ = load_data_for_year(previous_sy)
    except Exception:
        return go.Figure().update_layout(title="No data available", title_font=PLOT_TITLE)

    df_sy_n = data_curr.copy()
    df_sy_n1 = data_prev.copy()

    if selected_regions:
        df_sy_n = df_sy_n[df_sy_n['Region'].isin(selected_regions)]
        df_sy_n1 = df_sy_n1[df_sy_n1['Region'].isin(selected_regions)]

    def gender_filter(df, grade_base):
        if selected_gender == 'Male':
            cols = [f"{grade_base} Male"]
        elif selected_gender == 'Female':
            cols = [f"{grade_base} Female"]
        else:
            cols = [f"{grade_base} Male", f"{grade_base} Female"]
        return df[cols].sum().sum() if all(col in df.columns for col in cols) else 0

    if df_sy_n1.empty:
        tr_elem_jhs = 0
        tr_jhs_shs = 0
    else:
        g6 = gender_filter(df_sy_n1, "G6")
        g7 = gender_filter(df_sy_n, "G7")
        tr_elem_jhs = (g7 / g6) * 100 if g6 else 0

        g10 = gender_filter(df_sy_n1, "G10")
        g11_cols = [col for col in df_sy_n.columns if "G11" in col and (selected_gender in col or selected_gender == 'All')]
        g11 = df_sy_n[g11_cols].sum().sum() if g11_cols else 0
        tr_jhs_shs = (g11 / g10) * 100 if g10 else 0

    fig = go.Figure()

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type":"indicator"}, {"type":"indicator"}]],
        horizontal_spacing=0.15
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=tr_elem_jhs,
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "var(--primary-color)"}},
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=tr_jhs_shs,
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "var(--secondary-color)"}},
        ),
        row=1, col=2
    )

    fig.update_layout(
        annotations=[
            dict(
                text="Elementary<br>to High School",
                x=0.07, y=0.12,
                xref="paper", yref="paper",
                showarrow=False,
                font={"size": 14}
            ),
            dict(
                text="High School<br>to Senior High",
                x=0.95, y=0.12,
                xref="paper", yref="paper",
                showarrow=False,
                font={"size": 14}
            ),
        ],
        title={
            "text": "Transition Rate",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,
            "yanchor": "top"
        },
        margin={"t": 20, "b": 30, "l": 20, "r": 30},
        height=360,
        autosize=True,
        title_font=PLOT_TITLE
    )

    return fig


@app.callback(
    Output('k_to_12_distribution_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('school_year_filter', 'value')
)

def update_k_to_12_distribution(selected_regions, selected_gender, selected_school_year):
    if not selected_school_year:
        raise dash.exceptions.PreventUpdate
    try:
        data, grade_columns, _, _ = load_data_for_year(selected_school_year)
    except FileNotFoundError:
        raise dash.exceptions.PreventUpdate
     
    filtered = data.copy()

    if selected_regions:
        filtered = filtered[filtered['Region'].isin(selected_regions)]

    # Define grade groupings
    level_order = ['K', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'Elem NG',
                   'G7', 'G8', 'G9', 'G10', 'JHS NG', 'G11', 'G12']
    level_labels = {
        'K': 'Kinder', 'G1': 'Grade 1', 'G2': 'Grade 2', 'G3': 'Grade 3', 'G4': 'Grade 4',
        'G5': 'Grade 5', 'G6': 'Grade 6', 'Elem NG': 'NG-ES', 'G7': 'Grade 7',
        'G8': 'Grade 8', 'G9': 'Grade 9', 'G10': 'Grade 10', 'JHS NG': 'NG-JHS',
        'G11': 'Grade 11', 'G12': 'Grade 12'
    }

    level_group = {
        'K': 'ES', 'G1': 'ES', 'G2': 'ES', 'G3': 'ES', 'G4': 'ES', 'G5': 'ES', 'G6': 'ES', 'Elem NG': 'ES',
        'G7': 'JHS', 'G8': 'JHS', 'G9': 'JHS', 'G10': 'JHS', 'JHS NG': 'JHS',
        'G11': 'SHS', 'G12': 'SHS'
    }

    records = []
    for level in level_order:
        if level in ['G11', 'G12']:
            male_cols = [col for col in data.columns if col.startswith(level) and 'Male' in col]
            female_cols = [col for col in data.columns if col.startswith(level) and 'Female' in col]
        else:
            male_cols = [col for col in data.columns if col == f"{level} Male"]
            female_cols = [col for col in data.columns if col == f"{level} Female"]



        if selected_gender == 'Male':
            total = filtered[male_cols].sum().sum()
        elif selected_gender == 'Female':
            total = filtered[female_cols].sum().sum()
        else:
            total = filtered[male_cols + female_cols].sum().sum()

        records.append({
            'Level': level_labels[level],
            'Enrollment': total,
            'Group': level_group[level]
        })

    dist_df = pd.DataFrame(records)

    group_map = {
        'ES': 'Elementary School',
        'JHS': 'Junior High School',
        'SHS': 'Senior High School'
    }

    dist_df['Group Label'] = dist_df['Group'].map(group_map)

    dist_df['Display Enrollment'] = dist_df['Enrollment'].apply(
    lambda x: x + 30000 if x < 100000 else x
    )

    fig = px.bar(
        dist_df,
        x='Level',
        y='Display Enrollment',
        color='Group',
        category_orders={'Level': list(level_labels.values())},
        color_discrete_map={'ES': '#0a4485', 'JHS': '#BFDBFE', 'SHS': '#DE082C'},
        custom_data=['Group Label', 'Level', 'Enrollment'],  
        title='Enrollment Across Grade and Non Grade Levels',
        text='Enrollment'
    )

    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker_line_width=0,
        hovertemplate=(
        "Group: %{customdata[0]}<br>" +
        "Level: %{customdata[1]}<br>" +
        "Enrollment: %{customdata[2]:,}<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Enrollment',
        font=dict(size=13),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center'),
        bargap=0.2,
        title_font=PLOT_TITLE,
    )

    return fig

with open('ph.json', 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

# Mapping of DataFrame regions to GeoJSON regions
region_mapping = {
    'BARMM': 'Autonomous Region in Muslim Mindanao',
    'CAR': 'Cordillera Administrative Region',
    'CARAGA': 'Caraga',
    'MIMAROPA': 'Mimaropa',
    'NCR': 'National Capital Region',
    'Region I': 'Ilocos',
    'Region II': 'Cagayan Valley',
    'Region III': 'Central Luzon',
    'Region IV-A': 'Calabarzon',
    'Region V': 'Bicol',
    'Region VI': 'Western Visayas',
    'Region VII': 'Central Visayas',
    'Region VIII': 'Eastern Visayas',
    'Region IX': 'Zamboanga Peninsula',
    'Region X': 'Northern Mindanao',
    'Region XI': 'Davao',
    'Region XII': 'Soccsksargen'
}

import plotly.graph_objects as go

from dash import Input, Output

# Precompute all grade‑gender columns once
grade_columns = [
    col for col in data.columns
    if any(col.startswith(prefix) for prefix in
           ['K', 'G1','G2','G3','G4','G5','G6','Elem','JHS','G7','G8','G9','G10','G11','G12'])
    and ('Male' in col or 'Female' in col)
]

@app.callback(
    Output('enrollment_choropleth_map', 'figure'),
    [
        Input('school_year_filter', 'value'),
        Input('region_filter',       'value'),
        Input('grade_filter',        'value'),
        Input('gender_filter',       'value'),
    ]
)
def update_enrollment_choropleth(selected_school_year, selected_regions, selected_grades, selected_gender):
    # 1) Copy + filter by School Year
    if not selected_school_year:
        raise dash.exceptions.PreventUpdate
    try:
        data, grade_columns, _, _ = load_data_for_year(selected_school_year)
    except FileNotFoundError:
        raise dash.exceptions.PreventUpdate
    
    df = data.copy()
    # 3) Build lists of grade‑gender columns
    selected_cols_male   = []
    selected_cols_female = []

    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                # include all subject‑specific columns for those grades
                selected_cols_male   += [c for c in grade_columns if c.startswith(grade) and 'Male' in c]
                selected_cols_female += [c for c in grade_columns if c.startswith(grade) and 'Female' in c]
            else:
                selected_cols_male.append(f"{grade} Male")
                selected_cols_female.append(f"{grade} Female")
    else:
        # no grade selected → default to all
        selected_cols_male   = [c for c in grade_columns if 'Male'   in c]
        selected_cols_female = [c for c in grade_columns if 'Female' in c]

    # 4) Sum up based on gender filter
    if selected_gender == 'Male':
        df['Selected Grades Total'] = df[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        df['Selected Grades Total'] = df[selected_cols_female].sum(axis=1)
    else:  # 'All'
        df['Selected Grades Total'] = df[selected_cols_male + selected_cols_female].sum(axis=1)

    # 5) Drop schools with zero enrollment in selection
    df = df[df['Selected Grades Total'] > 0]

    # 6) Aggregate by Region
    #    (and remap region names if you need)
    df['Region'] = df['Region'].apply(lambda x: region_mapping.get(x, x))
    full_enrollment = (
        df
        .groupby('Region', as_index=False)['Selected Grades Total']
        .sum()
        .rename(columns={'Selected Grades Total': 'Total Enrollment'})
    )

    # 7) Apply region filter for the overlay
    if selected_regions:
        mapped = [region_mapping.get(r, r) for r in selected_regions]
        region_enrollment = full_enrollment[full_enrollment['Region'].isin(mapped)]
    else:
        region_enrollment = full_enrollment.copy()

    # First, get the original region codes from your dataset
    region_enrollment['Region Code'] = region_enrollment['Region'].map(
        {v: k for k, v in region_mapping.items()}
    )

    # Then build the hover label
    region_enrollment['Region Hover Label'] = region_enrollment.apply(
        lambda row: f"{row['Region Code']} ({row['Region']})" 
        if pd.notnull(row['Region Code']) else row['Region'],
        axis=1
    )

    # 8) Build layered choropleth
    fig = go.Figure()

    # base layer (grey)
    fig.add_choropleth(
        geojson=geojson_data,
        locations=full_enrollment['Region'],
        z=[0]*len(full_enrollment),
        featureidkey='properties.name',
        colorscale=[[0,'lightgrey'],[1,'lightgrey']],
        showscale=False,
        marker_line_width=0.5,
        marker_line_color='white',
        hoverinfo='skip',   # prevents hover box
        name=''             # removes "trace 1"
    )

    # overlay with actual totals
    fig.add_choropleth(
        geojson=geojson_data,
        locations=region_enrollment['Region'],
        z=region_enrollment['Total Enrollment'],
        featureidkey='properties.name',
        colorbar_title="Total Enrollment",
        coloraxis="coloraxis",
        customdata=region_enrollment[['Region Hover Label']].values,
        hovertemplate = "%{customdata[0]}<br>Students: %{z:,} <extra></extra>"
    )

    fig.update_layout(
        coloraxis=dict(
            colorscale="Viridis",
            cmin=full_enrollment['Total Enrollment'].min(),
            cmax=full_enrollment['Total Enrollment'].max()
        ),
        title="Regional Enrollment",
        height=500,
        geo=dict(fitbounds="locations", visible=False),
        margin={"r":0,"t":50,"l":0,"b":0},
        dragmode=False,
        autosize=True,

        title_font=PLOT_TITLE,

        annotations=[
        dict(
            x=0.5,  # Position of the subheading (centered horizontally)
            y=0,  # Position below the title (adjust as necessary)
            text="This map visualizes the learner distribution across all regions in the Philippines.",
            showarrow=False,
            font=dict(
                size=14,
                color="gray"
            ),
            align="center"
        )
    ]
    )

    return fig

# Callback for updating Stacked bar chart of school offerings by COC
@app.callback(
    Output('coc_sector_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_coc_sector_chart(selected_sy, selected_regions, selected_grades, selected_gender):
    # Make a copy of the full dataset
    df = data.copy()

    # Filter Dataset by selected school year
    df = df[df['School Year'] == selected_sy]

    # Filter Dataset to inlcude only those regions
    if selected_regions:
        df = df[df['Region'].isin(selected_regions)]

    # Initialize empty lists 
    selected_cols_male = []
    selected_cols_female = []

    # Dynamically determine which columns to sum based on selected grades
    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                # For G11 and G12, match all subject-specific Male/Female columns
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                # For lower grades, columns are named like "G1 Male", "G1 Female", etc.
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        # If no grades are selected, default to all available grade columns
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]
    
    # Compute total enrollment based on selected gender
    if selected_gender == 'Male':
        df['Selected Grades Total'] = df[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        df['Selected Grades Total'] = df[selected_cols_female].sum(axis=1)
    else:
        # If gender is "All", sum both male and female selected columns
        df['Selected Grades Total'] = df[selected_cols_male + selected_cols_female].sum(axis=1)

    # Filter out schools that have no enrollment in the selected grades and gender
    df = df[df['Selected Grades Total'] > 0]

    # Count schools by COC category and sector
    df_counts = (
        df
        .groupby(['Modified COC', 'Sector'])
        .size()
        .reset_index(name='Count')
    )
    # Ensure categories order
    coc_order = ['Purely ES', 'Purely JHS', 'Purely SHS', 'ES and JHS', 'JHS with SHS', 'All Offering']
    df_counts['Modified COC'] = pd.Categorical(df_counts['Modified COC'], categories=coc_order, ordered=True)
    df_counts = df_counts.sort_values('Modified COC')

    # Create stacked bar
    fig = px.bar(
        df_counts,
        x='Modified COC',
        y='Count',
        color='Sector',
        category_orders={
            'Modified COC': coc_order, 
            'Sector': ['Public', 'Private', 'SUCsLUCs'] # Order Sectors
            },
        labels={
            'Count': 'Number of Schools', 
            'Modified COC': 'COC Offering', 
            'Sector': 'Sector'},
        barmode='stack'
    )

    # Update the chart layout 
    fig.update_layout(
        title='School Offerings by Certificate of Completion (COC)<br>Type and Sector',
        xaxis_title='Type',
        yaxis_title='Number of Schools',
        font=dict(size=13),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend_title='Sector',
        margin=dict(l=40, r=20, t=80, b=40),
        height=350,
        title_font=PLOT_TITLE,
    )

    # Add custom colors for each sector
    for trace in fig.data:
        if trace.name == 'Public':
            trace.marker.color = '#0a4485'
        elif trace.name == 'Private':
            trace.marker.color = '#BFDBFE'
        elif trace.name == 'SUCsLUCs':
            trace.marker.color = '#DE082C'

    return fig

@app.callback(
    Output('enrollment_trend_line_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('stored_school_year', 'data')
)
def update_enrollment_trend_chart(selected_year, stored_year):
    if not selected_year:
        selected_year = stored_year

    available_years = get_available_school_years()
    if not available_years:
        return go.Figure().update_layout(title="No data available", title_font=PLOT_TITLE)

    if not selected_year:
        selected_year = "2023-2024" if "2023-2024" in available_years else available_years[-1]


    idx = available_years.index(selected_year)
    start = max(idx - 2, 0)
    end = min(idx + 3, len(available_years))
    years_to_load = available_years[start:end]

    frames = []
    for year in years_to_load:
        try:
            df, _, _, _ = load_data_for_year(year)
            frames.append(df[['School Year', 'Total Enrollment']])
        except Exception:
            continue

    if not frames:
        return go.Figure().update_layout(
            title="No data available for selected range",
            xaxis_title='School Year',
            yaxis_title='Total Enrollment'
        )

    df_combined = pd.concat(frames)
    grouped = df_combined.groupby(['School Year'], as_index=False)['Total Enrollment'].sum()
    grouped = grouped.sort_values(by='School Year')

    if grouped.empty:
        return px.line(title="No data to display")

    try:
        fig = px.line(
            grouped,
            x='School Year',
            y='Total Enrollment',
            title='Total Enrollment Trend<br>Over the Years',
            markers=True
        )

        fig.update_layout(
            title='Total Enrollment Trend<br>Over the Years',
            font=dict(size=13),
            plot_bgcolor='white',
            height=350,
            paper_bgcolor='white',
            title_font=PLOT_TITLE,
            xaxis_title='School Year',
            yaxis_title='Total Enrollment',
            xaxis=dict(tickmode='linear'),
            yaxis=dict(title='Total Enrollment')
        )
        return fig
    except Exception as e:
        print("Error rendering Enrollment Trend chart:", e)
        return px.line(title="Error rendering Enrollment Trend chart")
    
@app.callback(
    Output('up_sned_sector_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value')
)
def update_sned_sector_chart(selected_year, selected_regions):
    filtered_df = data.copy()

    if selected_year:
        filtered_df = filtered_df[filtered_df['School Year'] == selected_year]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

    # Ensure 'School Name' column does not contain NaN before applying string methods
    filtered_df = filtered_df.dropna(subset=['School Name'])

    # Filter the DataFrame for schools with "SPED Center" in the name
    sped_centers = filtered_df[filtered_df['School Name'].str.lower().str.contains('sped center')]

    # Select the relevant columns for male and female enrollments
    male_cols = [col for col in sped_centers.columns if 'Male' in col]
    female_cols = [col for col in sped_centers.columns if 'Female' in col]

    # Fill NaN values with 0 for the male and female enrollment columns before summing
    sped_centers[male_cols] = sped_centers[male_cols].fillna(0)
    sped_centers[female_cols] = sped_centers[female_cols].fillna(0)

    # Calculate SNed_Male and SNed_Female by summing the relevant columns
    sped_centers['SNed_Male'] = sped_centers[male_cols].sum(axis=1)
    sped_centers['SNed_Female'] = sped_centers[female_cols].sum(axis=1)

    # Calculate total enrollment by school
    sped_centers['Total_Enrollment'] = sped_centers[['SNed_Male', 'SNed_Female']].sum(axis=1)

    # Group by region and school name and get the top 5 schools with SPED Center in their name
    top_5_sped_centers = sped_centers.groupby(['Region', 'School Name'])['Total_Enrollment'].sum().reset_index()

    # Get the top 5 schools by total enrollment per region
    top_5_sped_centers = top_5_sped_centers.groupby('Region').apply(lambda x: x.nlargest(5, 'Total_Enrollment')).reset_index(drop=True)

    # Create the bar chart showing the top 5 schools per region
    fig = px.bar(
        top_5_sped_centers,
        x='Region',
        y='Total_Enrollment',
        color='Region',
        text='School Name',
        title='Top 5 SPED Centers per Region by Total Enrollment'
    )

    # Customizing layout for better clarity
    fig.update_layout(
        xaxis_title='Region',
        yaxis_title='Total Enrollment',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=13),
        height=600,
        margin=dict(l=20, r=20, t=80, b=40),
        title_font=PLOT_TITLE,
    )
    
    # Show the school names inside the bars
    fig.update_traces(texttemplate='%{text}', textposition='inside')

    return fig

# Manual Data Page

@app.callback(
    Output('input_division', 'options'),
    Output('input_division', 'disabled'),
    Input('input_region', 'value')
)
def update_divisions(region):
    if not region:
        return [], True
    schools_df = load_schools()
    filtered = schools_df[schools_df['Region'] == region]
    return [{'label': d, 'value': d} for d in sorted(filtered['Division'].dropna().unique())], False

@app.callback(
    Output('input_school_name', 'options'),
    Output('input_school_name', 'disabled'),
    Input('input_division', 'value')
)
def update_schools(division):
    if not division:
        return [], True
    schools_df = load_schools()
    filtered = schools_df[schools_df['Division'] == division]
    return [{'label': s, 'value': s} for s in sorted(filtered['School Name'].dropna().unique())], False


@app.callback(
    Output('beis_school_id_display', 'value'),
    Output('auto_barangay', 'value'),
    Output('auto_sector', 'value'),
    Output('auto_subclassification', 'value'),
    Output('auto_type', 'value'),
    Output('auto_coc', 'value'),
    Input('input_school_name', 'value')
)
def autofill_fields(school_name):
    if not school_name:
        return [""] * 6
    schools_df = load_schools()
    school = schools_df[schools_df['School Name'] == school_name].iloc[0]
    return (
        school["BEIS School ID"],
        school["Barangay"],
        school["Sector"],
        school["School Subclassification"],
        school["School Type"],
        school["Modified COC"]
    )

# === CALLBACK: Finalize Submission ===
@app.callback(
    Output("submission_feedback", "children"),
    Output("upload-feedback", "children"),
    Output("refresh_school_year_trigger", "data", allow_duplicate=True),
    Input("finalize-submit", "n_clicks"),
    State("input_school_name", "value"),
    State("input_school_year", "value"),
    State("input_grade", "value"),
    State("input_enrollment_male", "value"),  # Male enrollment count
    State("input_enrollment_female", "value"),  # Female enrollment count
    State("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-school-year-dropdown", "value"),
    prevent_initial_call=True
)
def finalize_submission(
    n_clicks, school_name, manual_year, grade, male_count, female_count,
    upload_contents, upload_filename, upload_year
):
    import os, base64, io, pandas as pd, time

    # Handle Upload Mode
    if upload_contents and upload_year:
        try:
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df['School Year'] = upload_year

            # Add missing columns
            for col in correct_columns:
                if col not in df.columns:
                    df[col] = "N/A"
            df = df[correct_columns]
            df = df.fillna("N/A").replace(0, "N/A")

            output_filename = f"data_{upload_year}.csv"
            output_path = os.path.join("data_files", output_filename)
            df.to_csv(output_path, index=False, na_rep="N/A")

            # Handle new schools
            schools_path = os.path.join("data_files", "schools.csv")
            existing_schools_df = pd.read_csv(schools_path)
            existing_ids = set(existing_schools_df["BEIS School ID"].astype(str))

            uploaded_ids = df["BEIS School ID"].astype(str)
            new_ids = [sid for sid in uploaded_ids.unique() if sid not in existing_ids]
            if new_ids:
                school_cols = existing_schools_df.columns
                new_school_rows = df[df["BEIS School ID"].astype(str).isin(new_ids)][school_cols.intersection(df.columns)]
                for col in school_cols:
                    if col not in new_school_rows.columns:
                        new_school_rows[col] = "N/A"
                new_school_rows = new_school_rows[school_cols].fillna("N/A").replace(0, "N/A")
                updated_schools_df = pd.concat([existing_schools_df, new_school_rows], ignore_index=True)
                updated_schools_df.to_csv(schools_path, index=False, na_rep="N/A")

            return "", f"✅ Upload finalized for {upload_year}.", upload_year

        except Exception as e:
            return "", f"❌ Upload failed: {str(e)}", dash.no_update

    # Handle Manual Mode
    elif school_name and manual_year and grade and (male_count or female_count):  # Check if at least one count is provided
        try:
            # Process the manual entry
            meta = get_school_metadata(school_name)
            school_id = meta["BEIS School ID"]
            filename = f"data_{manual_year}.csv"
            file_path = os.path.join("data_files", filename)
            df = pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame(columns=correct_columns)

            for col in correct_columns:
                if col not in df.columns:
                    df[col] = "N/A"
            df = df[correct_columns]

            match = (df['School Year'] == manual_year) & (df['BEIS School ID'] == school_id)
            if not match.any():
                new_row = {col: "N/A" for col in correct_columns}
                new_row["School Year"] = manual_year
                new_row["BEIS School ID"] = school_id
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                row_idx = df.index[-1]
            else:
                row_idx = df[match].index[0]

            if male_count:
                column_name = f"{grade} Male"
                if column_name not in df.columns:
                    df[column_name] = "N/A"
                existing = df.at[row_idx, column_name]
                existing = 0 if pd.isna(existing) or existing == "N/A" else int(existing)
                df.at[row_idx, column_name] = existing + male_count

            if female_count:
                column_name = f"{grade} Female"
                if column_name not in df.columns:
                    df[column_name] = "N/A"
                existing = df.at[row_idx, column_name]
                existing = 0 if pd.isna(existing) or existing == "N/A" else int(existing)
                df.at[row_idx, column_name] = existing + female_count

            df.to_csv(file_path, index=False, na_rep="N/A")

            return f"✅ Enrollment saved for {manual_year}.", "", manual_year

        except Exception as e:
            return f"❌ Error: {str(e)}", "", dash.no_update

    else:
        return "⚠️ Incomplete manual input. Please ensure at least one enrollment field (Male or Female) is filled.", "", dash.no_update




# === CALLBACK: Check Missing Fields ===
@app.callback(
    Output("missing-fields-modal", "is_open", allow_duplicate=True),
    Output("missing-fields-message", "children", allow_duplicate=True),
    Input("submit_button", "n_clicks"),
    State("input_school_name", "value"),
    State("input_school_year", "value"),
    State("input_grade", "value"),
    State("input_enrollment_male", "value"),  # Male enrollment
    State("input_enrollment_female", "value"),  # Female enrollment
    prevent_initial_call=True
)
def check_missing_fields(n_clicks, name, year, grade, male_count, female_count):
    if n_clicks:
        # Check if any required fields are missing
        missing_fields = []
        if not name:
            missing_fields.append("School Name")
        if not year:
            missing_fields.append("School Year")
        if not grade:
            missing_fields.append("Grade Level")
        
        # Check if both male and female enrollment counts are missing
        if not male_count and not female_count:
            missing_fields.append("Male and/or Female Enrollment Count")

        if missing_fields:
            missing_message = "⚠️ The following fields are missing: " + ", ".join(missing_fields) + ".<br><br>Please fill them in."
            return True, dcc.Markdown(missing_message, dangerously_allow_html=True)  # Show in Missing Fields Modal
        else:
            return False, ""  # No missing fields, modal remains closed
    return False, ""


@app.callback(
    Output("missing-fields-modal", "is_open"),
    Input("close-missing-fields-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_missing_fields_modal(n_clicks):
    if n_clicks:
        return False  # Close the modal
    return True  # Keep it open if the button isn't clicked


# === CALLBACK: Open Confirm Modal on Submit ===
@app.callback(
    Output("confirm-modal", "is_open", allow_duplicate=True),
    Output("confirm-message", "children", allow_duplicate=True),
    Output("confirm-checkbox", "value", allow_duplicate=True),
    Input("submit_button", "n_clicks"),
    State("input_school_name", "value"),
    State("input_school_year", "value"),
    State("input_grade", "value"),
    State("input_enrollment_male", "value"),  # Male enrollment
    State("input_enrollment_female", "value"),  # Female enrollment
    prevent_initial_call=True
)
def open_modal_manual_submit(n_clicks, name, year, grade, male_count, female_count):
    if n_clicks:
        # Check if all fields are filled and that one of the gender counts is entered
        if not all([name, year, grade]):
            return False, "⚠️ Please fill in all fields before submitting.", False  # Don't open the confirmation modal

        # If neither male nor female enrollment count is filled
        if not male_count and not female_count:
            return False, "⚠️ Please fill in the Male or Female enrollment count.", False  # Don't open the confirmation modal

        return True, f"Are you sure you want to submit data for {year}?", False  # Open the confirmation modal
    return False, "", False


# === CALLBACK: Handle File Upload Modal ===
@app.callback(
    Output("upload-modal", "is_open", allow_duplicate=True),
    Output("upload-feedback", "children", allow_duplicate=True),
    Output("finalize-submit", "disabled", allow_duplicate=True),  # Re-enable Finalize button
    Input("upload-data", "contents"),
    State("upload-school-year-dropdown", "value"),
    prevent_initial_call=True
)
def open_modal_upload(contents, upload_year):
    if contents and upload_year:
        # You can simply remove the filename from being returned in the feedback
        return True, "File uploaded successfully", False  # Enable Finalize button
    return False, "", False  # Keep Finalize button disabled initially


# === CALLBACK: Handle Submit Button in Upload Modal ===
@app.callback(
    Output("confirm-modal", "is_open", allow_duplicate=True),
    Output("confirm-message", "children", allow_duplicate=True),
    Output("confirm-checkbox", "value", allow_duplicate=True),
    Input("submit-upload", "n_clicks"),
    State("upload-filename", "children"),
    prevent_initial_call=True
)
def handle_upload_submit(n_clicks, filename):
    if n_clicks:
        return True, f"Are you sure you want to upload the CSV file?", False
    return False, "", False


# === CALLBACK: Close Modal from Cancel in Confirm Modal ===
@app.callback(
    Output("confirm-modal", "is_open", allow_duplicate=True),
    Output("confirm-message", "children", allow_duplicate=True),
    Output("confirm-checkbox", "value", allow_duplicate=True),
    Input("close-confirm-modal", "n_clicks"),
    State("confirm-modal", "is_open"),
    prevent_initial_call=True
)
def close_modal(n_clicks, is_open):
    if n_clicks:
        return False, "", False  # Close modal when cancel is clicked
    return is_open, "", False  # Keep modal open if cancel is not clicked


# === CALLBACK: Close Modal from Cancel (including file reset) ===
@app.callback(
    Output("confirm-modal", "is_open", allow_duplicate=True),
    Output("confirm-message", "children", allow_duplicate=True),
    Output("confirm-checkbox", "value", allow_duplicate=True),
    Output("upload-data", "contents", allow_duplicate=True),  # Reset file input
    Input("close-upload-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_upload_modal(n_clicks):
    if n_clicks:
        return False, "", False, None  # Close the modal and reset the file input
    return True, "", False, None  # Keep the modal open if the button isn't clicked


# === CALLBACK: Enable/disable Finalize button ===
@app.callback(
    Output("finalize-submit", "disabled", allow_duplicate=True),
    Input("confirm-checkbox", "value"),
    prevent_initial_call=True
)
def toggle_finalize_button(checked):
    return not checked

# === CALLBACK: Finalize Button to Close Modals ===
@app.callback(
    Output("confirm-modal", "is_open", allow_duplicate=True),
    Output("upload-modal", "is_open", allow_duplicate=True),
    Output("finalize-submit", "disabled", allow_duplicate=True),
    Input("finalize-submit", "n_clicks"),
    prevent_initial_call=True
)
def finalize_submission(n_clicks):
    if n_clicks:
        return False, False, True  # Close both modals and disable finalize button
    return True, True, False  # Keep modals open if finalize hasn't been clicked

@app.callback(
    Output('table_school_year', 'options'),
    Output('table_school_year', 'value'),
    Input('refresh_school_year_trigger', 'data'),
    prevent_initial_call=False
)
def refresh_school_year_options(trigger_data):
    years = get_available_school_years()
    years.sort()

    options = [{'label': y, 'value': y} for y in years]

    if not years:
        return [], None

    # 👇 Use triggered year if available and valid
    default_year = trigger_data if trigger_data in years else years[-1]

    return options, default_year

@app.callback(
    Output('enrollment_table', 'data'),
    Output('enrollment_table', 'columns'),
    Input('table_school_year', 'value')  # <- ONLY input needed
)
def update_enrollment_table(school_year):
    file_path = f"data_files/data_{school_year}.csv"
    if not os.path.exists(file_path):
        return [], []

    df = pd.read_csv(file_path)

    from app_data import load_schools
    schools_df = load_schools()

    numeric_df = df.copy()
    if "BEIS School ID" in numeric_df.columns and "BEIS School ID" in schools_df.columns:
        numeric_df = numeric_df.merge(schools_df[["BEIS School ID", "Region", "Division"]], on="BEIS School ID", how="left")
    else:
        raise KeyError("The 'BEIS School ID' column is missing in one of the DataFrames.")

    numeric_df = numeric_df.apply(pd.to_numeric, errors='ignore')

    male_cols = [col for col in df.columns if "Male" in col]
    female_cols = [col for col in df.columns if "Female" in col]

    numeric_df["Total Male"] = numeric_df[male_cols].replace("N/A", 0).apply(pd.to_numeric, errors='coerce').sum(axis=1)
    numeric_df["Total Female"] = numeric_df[female_cols].replace("N/A", 0).apply(pd.to_numeric, errors='coerce').sum(axis=1)
    numeric_df["Total Enrollment"] = numeric_df["Total Male"] + numeric_df["Total Female"]

    summary = numeric_df.groupby(["Region", "Division"], as_index=False)[["Total Male", "Total Female", "Total Enrollment"]].sum()

    return summary.to_dict("records"), [{"name": col, "id": col} for col in summary.columns]


@app.callback(
    Output("upload-modal", "is_open"),
    [Input("open-upload-modal", "n_clicks"),
     Input("close-upload-modal", "n_clicks")],
    [State("upload-modal", "is_open")]
)
def toggle_upload_modal(open_click, close_click, is_open):
    if open_click or close_click:
        return not is_open
    return is_open

if __name__ == "__main__":
    app.run(debug=True)

@app.callback(
    Output("user-avatar-img", "src"),
    Input("upload-photo", "contents"),
    State("upload-photo", "filename"),
    prevent_initial_call=True
)
def save_uploaded_avatar(contents, filename):
    if contents and filename:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        save_path = os.path.join("assets", "avatars", filename)

        # Save the file to the avatars directory
        with open(save_path, "wb") as f:
            f.write(decoded)

        return f"/assets/avatars/{filename}"

    raise dash.exceptions.PreventUpdate