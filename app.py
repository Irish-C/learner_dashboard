import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import json
import os
import hashlib
from datetime import datetime
import time

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

from layout.pages.manage_data import manage_data_content

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
school_year_options = [{'label': f"{y}-{y+1}", 'value': f"{y}-{y+1}"} for y in range(current_year - 10, current_year + 2)]

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
            return {"logged_in": True, "user": f"{first_name} {last_name}"}, ""

    return dash.no_update, "❌ Invalid credentials. Please try again."

# Callback to toggle sidebar
@app.callback(
    Output("sidebar-container", "children", allow_duplicate=True), 
    Output("content", "style"), 
    Output("sidebar-toggle-state", "data"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-toggle-state", "data"), 
    State("current-page", "data"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, is_collapsed, current_page):
    if n_clicks:
        is_collapsed = not is_collapsed
    
    # Update sidebar with new collapsed state and current page
    updated_sidebar = create_sidebar(is_collapsed=is_collapsed, current_page=current_page)
    
    # Update content margin
    content_style = get_content_style(is_collapsed)
    
    return [updated_sidebar], content_style, is_collapsed

@app.callback(
    Output("content", "children"), 
    Output("current-page", "data"), 
    Output("sidebar-container", "children"),
    Input("btn-1", "n_clicks"),
    Input("btn-2", "n_clicks"),
    Input("btn-3", "n_clicks"),
    Input("btn-4", "n_clicks"),
    State("current-page", "data"), 
    State("sidebar-toggle-state", "data")
)
def change_page(btn1, btn2, btn3, btn4, current_page, is_collapsed):
    ctx = callback_context
    if not ctx.triggered:
        return (
            create_content(current_page, data, grade_options, region_options, combined_shs_track_df, school_year_options),
            current_page,
            create_sidebar(is_collapsed=is_collapsed, current_page=current_page)
        )
    
    # Determine which button was clicked
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    button_to_page = {
        "btn-1": PAGE_CONSTANTS[1],
        "btn-2": PAGE_CONSTANTS[2],
        "btn-3": PAGE_CONSTANTS[3],
        "btn-4": PAGE_CONSTANTS[4],
    }
    selected_page = button_to_page.get(button_id, PAGE_CONSTANTS.get(1, current_page))  # Fallback to default page if button ID is unexpected
    
    # Fallback to current page if something unexpected happens
    selected_page = button_to_page.get(button_id, current_page)
    
    return (
        create_content(selected_page, data, grade_options, region_options, combined_shs_track_df, school_year_options),
        selected_page,
        create_sidebar(is_collapsed=is_collapsed, current_page=selected_page)
    )

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
        'border': '1px solid #ccc'
    }

    if login_data["logged_in"]:
        first_name = login_data.get("user").split()[0]
        print(f"Stored first name: {first_name}")  # Debug print to ensure the first name is stored
        return html.Div(
            className="body-style",
            children=[
                dcc.Store(id='sidebar-toggle-state', data=False),
                dcc.Store(id='current-page', data="dashboard"),
                dcc.Store(id='user-first-name', data=first_name),  # Store the first name
                create_header(),
                html.Div(
                    className="app-container",
                    children=[
                        html.Div(id="sidebar-container", children=[
                            create_sidebar(is_collapsed=False, current_page="dashboard")
                        ]),
                        html.Div(id="content", style=get_content_style(False), children=create_content(
                            "dashboard", data, grade_options, region_options, combined_shs_track_df, school_year_options 
                        ))
                    ]
                )
            ]
        )
    return html.Div(
    style={
        "height": "100vh",
        "width": "100%",
        "backgroundImage": 'url("/assets/icons/classroom.png")',
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
                html.Img(src="/assets/icons/LIST.png", style={"height": "120px", "marginBottom": "10px"}),
                html.H4("LEARNER INFORMATION SYSTEM", style={
                    "fontWeight": "bold",
                    "letterSpacing": "2px",
                    "fontSize": "16px",
                    "fontFamily": "Roboto, sans-serif",
                    "marginBottom": "20px"
                })
            ], style={"textAlign": "center"}),

            # Input Fields
            dcc.Store(id='user-first-name', data={}),
            dbc.Input(id="input-firstname", placeholder="First Name", type="text", className="mb-3", style={"fontFamily": "Roboto, sans-serif"}),
            dbc.Input(id="input-lastname", placeholder="Last Name", type="text", className="mb-3", style={"fontFamily": "Roboto, sans-serif"}),
            dbc.Input(id="input-email", placeholder="Email Address", type="email", className="mb-3", style={"fontFamily": "Roboto, sans-serif"}),
            html.Div([dbc.Input(id="input-password", type="password", placeholder="Password", className="w-100"),
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
                        "color": "#888"
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
            "justifyContent": "flex-start" 
        })
    ]
)


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
        color_discrete_sequence=['#b0cfff', '#f9c9e2']
    )

    pie_chart.update_traces(textinfo='percent')

    pie_chart.update_layout(
        margin=dict(t=30, b=0, l=0, r=0),
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif" 
        ),
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
        name='Total Enrollment'
    ), secondary_y=False)

    fig_combo.add_trace(go.Scatter(
        x=agg_division['Division'],
        y=agg_division['Number of Schools'],
        name='Number of Schools',
        mode='lines+markers'
    ), secondary_y=True)

    fig_combo.update_layout(
        title='Top 15 Divisions: Total Enrollment and Number of Schools',
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif"
        ),
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
    total_schools = sector_counts.sum()
    sector_percentage = (sector_counts / total_schools) * 100

    # Format percentages for each sector
    public_percentage = sector_percentage.get('Public', 0)
    private_percentage = sector_percentage.get('Private', 0)
    sucs_lucs_percentage = sector_percentage.get('SUCsLUCs', 0) 


    # KPI Cards (now with Sector card inside the 4-col row)
    card_style = {
        "height": "175px",
        "border": "none",
        "borderRadius": "10px",
        "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
        "padding": "10px",
        
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
                        html.I(className="fas fa-user-graduate", style={"fontSize": "30px", "color": "#008000", "marginBottom": "10px"}),
                        html.H5("Total Enrolled", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H2(f"{total_students:,}", style={"color": "#008000", "margin": "0"})
                    ], style=text_style)
                ]),
                color="white",#d1ffbd
                style={**card_style, "borderBottom": "5px solid #28a745"}
            ),
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-school", style={"fontSize": "30px", "color": "#FBC02D", "marginBottom": "10px"}),
                        html.H5("Total Schools", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H2(f"{total_schools:,}", style={"color": "#FBC02D", "margin": "0"})
                    ], style=text_style)
                ]),
                color="white",#ffffc5
                style={**card_style, "borderBottom": "5px solid #ffc107"}
            ),
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-map-marked-alt", style={"fontSize": "35px", "color": "#e74c3c", "marginBottom": "10px"}),
                        html.H5("Most Enrolled Region as of (school year)", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H3(f"{most_enrolled_region}: {region_total/1000:.2f}k", style={"color": "#e74c3c", "margin": "0", "fontSize": "24px"})
                    ], style=text_style)
                ]),
                color="white",#ffcccb
                style={**card_style, "borderBottom": "5px solid #e74c3c"}
            ),
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chalkboard-teacher", style={"fontSize": "35px", "color": "#3498db", "marginBottom": "10px"}),
                        html.H5("School Sector Ratio", style={"color": "var(--gray-color)", "margin": "0", "fontWeight": "bold"}),
                        html.H3(f"{public_percentage:.2f}% | {private_percentage:.2f}% | {sucs_lucs_percentage:.2f}%", style={"color": "#3498db", "margin": "0", "fontSize": "20px"})
                    ], style=text_style)
                ]),
                color="#white",#BFDBFE
                style={**card_style, "borderBottom": "5px solid #3498db"}
            ),
            width=3, style={"marginBottom": "15px", 'padding': "0.5rem"}
        )
    ], justify="center", align="start")

    # Standalone Most Enrolled Division Card
    most_enrolled_division_text = filtered_data.groupby('Division')['Selected Grades Total'].sum().idxmax()
    most_enrolled_division_card = html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-users-cog", style={"fontSize": "30px", "color": "#007BFF", "marginBottom": "0.5rem"}),
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
def update_shs_track_chart(selected_year, selected_regions, selected_gender):
    df_filtered = combined_shs_track_df.copy()

    # 🧠 Filter by school year
    if selected_year:
        df_filtered = df_filtered[df_filtered['School Year'] == selected_year]

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

    # 📊 Plot the chart safely
    try:
        fig = px.bar(
            grouped,
            x='Total Enrollment',
            y='Track',
            color='Grade Level',
            orientation='h',
            text='Total Enrollment',
            title='Senior High Track Enrollment Overview'
        )

        fig.update_layout(
            title='Senior High Track Enrollment Overview',
            font=dict(size=13),
            height=350,
            scene=dict(
                xaxis_title='Track',
                yaxis_title='Total Enrollment',
                zaxis_title='Grade Level'
            ),
            title_font=dict(
                size=20,  
                color="var(--gray-color)",  
                family="Arial, sans-serif"
            ),
        )
        return fig
    except Exception as e:
        print("SHS Chart Rendering Error:", e)
        return px.bar(title="Error rendering SHS Track chart")
    
@app.callback(
    Output('top_schools_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_top_schools_chart(selected_regions, selected_grades, selected_gender):
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
        'Public': '#3498db',
        'Private': '#e74c3c',
        'SUCsLUCs': '#f1c40f'
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
            ticksuffix='  '
        ),

        font=dict(size=13),
        legend=dict(orientation='h', y=-0.25, x=0.5, xanchor='center'),
        title_font=dict(
            size=20,  
            color="var(--gray-color)",
            family="Arial, sans-serif"
        ),
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
        title='Special Needs Education Enrollment by<br>School Sector and Gender'
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
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif"
        )
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
    df_sy_n = data[data['School Year'] == selected_sy]

    # Previous year setup (mocked)
    try:
        previous_sy = str(int(selected_sy.split('-')[0]) - 1) + '-' + str(int(selected_sy.split('-')[1]) - 1)
    except:
        previous_sy = "N/A"
    df_sy_n1 = data[data['School Year'] == previous_sy]

    if selected_regions:
        df_sy_n = df_sy_n[df_sy_n['Region'].isin(selected_regions)]
        df_sy_n1 = df_sy_n1[df_sy_n1['Region'].isin(selected_regions)]

    # Helper function
    def gender_filter(df, grade_base):
        if selected_gender == 'Male':
            cols = [f"{grade_base} Male"]
        elif selected_gender == 'Female':
            cols = [f"{grade_base} Female"]
        else:
            cols = [f"{grade_base} Male", f"{grade_base} Female"]
        return df[cols].sum().sum()

    # Placeholder logic if no prev year exists
    if df_sy_n1.empty:
        tr_elem_jhs = 0
        tr_jhs_shs = 0
    else:
        g6 = gender_filter(df_sy_n1, "G6")
        g7 = gender_filter(df_sy_n, "G7")
        tr_elem_jhs = (g7 / g6) * 100 if g6 else 0

        g10 = gender_filter(df_sy_n1, "G10")
        g11_cols = [col for col in df_sy_n.columns if "G11" in col and (selected_gender in col or selected_gender == 'All')]
        g11 = df_sy_n[g11_cols].sum().sum()
        tr_jhs_shs = (g11 / g10) * 100 if g10 else 0

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=tr_elem_jhs,
        domain={'x': [0, 0.5], 'y': [0, 1]},
        title={'text': "Elementary to High School"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#1f77b4"}}
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=tr_jhs_shs,
        domain={'x': [0.5, 1], 'y': [0, 1]},
        title={'text': "High School to Senior High"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#ff7f0e"}}
    ))

    fig.update_layout(
        title="Transition Rate (Placeholder as there are no previous year)", 
        height=300,
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif"
        )

        )
    return fig

@app.callback(
    Output('k_to_12_distribution_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('school_year_filter', 'value')
)
def update_k_to_12_distribution(selected_regions, selected_gender, selected_year):
    filtered = data.copy()

    if selected_year:
        filtered = filtered[filtered['School Year'] == selected_year]
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

    fig = px.bar(
        dist_df,
        x='Level',
        y='Enrollment',
        color='Group',
        category_orders={'Level': list(level_labels.values())},
        color_discrete_map={'ES': '#a3c4f3', 'JHS': '#2a6fdb', 'SHS': '#071952'},
        title='Enrollment Across Grade and Non Grade Levels',
        text='Enrollment'
    )

    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker_line_width=0
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Enrollment',
        font=dict(size=13),  # Set font size here
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center'),
        bargap=0.2,
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif"
        )
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
def update_enrollment_choropleth(selected_sy, selected_regions, selected_grades, selected_gender):
    # 1) Copy + filter by School Year
    df = data.copy()
    df = df[df['School Year'] == selected_sy]

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
        hoverinfo='none'
    )

    # overlay with actual totals
    fig.add_choropleth(
        geojson=geojson_data,
        locations=region_enrollment['Region'],
        z=region_enrollment['Total Enrollment'],
        featureidkey='properties.name',
        colorbar_title="Total Enrollment",
        coloraxis="coloraxis"
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

        title_font=dict(
            size=20,  # Similar size to your provided H5 (adjust as needed)
            color="var(--gray-color)",  # Matches the color in your example
            family="Arial, sans-serif"  # Default font
        ),

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
        title_font=dict(
            size=20,  
            color="var(--gray-color)",  
            family="Arial, sans-serif"
        )
    )

    return fig

@app.callback(
    Output('enrollment_trend_line_chart', 'figure'),
    Input('school_year_filter', 'value')  # Only the school year filter is used now
)
def update_enrollment_trend_chart(selected_year):
    df_filtered = data.copy()  # Replace with your actual DataFrame

    # 🧠 Filter by school year
    if selected_year:
        df_filtered = df_filtered[df_filtered['School Year'] == selected_year]

    # ✅ Final protection: prevent plotly from erroring on empty or malformed data
    if df_filtered.empty:
        return go.Figure().update_layout(
            title="No data available for the selected school year",
            xaxis_title='School Year',
            yaxis_title='Total Enrollment'
        )

    # 🧾 Group the data by 'School Year' and calculate total enrollment
    grouped = df_filtered.groupby(['School Year'], as_index=False)['Total Enrollment'].sum()

    # 🔐 Defensive: check again if grouped is empty
    if grouped.empty:
        return px.line(title="No data to display")
    
    # 📊 Plot the line chart safely
    try:
        fig = px.line(
            grouped,
            x='School Year',
            y='Total Enrollment',
            title='Total Enrollment Trend<br>Over the Years',
            markers=True  # Show markers at each data point on the line
        )

        fig.update_layout(
            title='Total Enrollment Trend<br>Over the Years',
            font=dict(size=13),
            plot_bgcolor='white',
            height=350,
            paper_bgcolor='white',
            title_font=dict(
                size=20,  
                color="var(--gray-color)",  # Match your CSS variable for gray color
                family="Arial, sans-serif"
            ),
            xaxis_title='School Year',
            yaxis_title='Total Enrollment',
            xaxis=dict(tickmode='linear'),  # Ensure proper linear ticks on x-axis
            yaxis=dict(title='Total Enrollment')
        )
        return fig
    except Exception as e:
        print("Error rendering Enrollment Trend chart:", e)
        return px.line(title="Error rendering Enrollment Trend chart")

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

@app.callback(
    Output('table_school_year', 'options'),
    Output('table_school_year', 'value'),
    Input('refresh_school_year_trigger', 'data'),
    prevent_initial_call=False
)
def refresh_school_year_options(trigger_data):
    years = get_available_school_years()
    years.sort()  # Ascending

    options = [{'label': y, 'value': y} for y in years]

    if trigger_data == "initial-load":
        default_year = "2023-2024" if "2023-2024" in years else (years[0] if years else None)
    else:
        default_year = trigger_data if trigger_data in years else (years[0] if years else None)

    return options, default_year


@app.callback(
    Output("submission_feedback", "children"),
    Output("refresh_school_year_trigger", "data"),
    Input("submit_button", "n_clicks"),
    State("input_school_name", "value"),
    State("input_school_year", "value"),
    State("input_grade", "value"),
    State("input_gender", "value"),
    State("input_enrollment", "value")
)
def submit_data(n_clicks, school_name, year, grade, gender, count):
    if not n_clicks:
        return "", dash.no_update
    if not all([school_name, year, grade, gender, count]):
        return "Please fill all fields."

    try:
        count = int(count)
        if count < 0:
            return "Enrollment count cannot be negative."
    except (ValueError, TypeError):
        return "Please enter a valid enrollment number."

    import os
    import pandas as pd

    meta = get_school_metadata(school_name)
    school_id = meta["BEIS School ID"]
    filename = f"data_{year}.csv"
    file_path = os.path.join("data_files", filename)

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

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=correct_columns)

    # Ensure all columns are initialized
    for col in correct_columns:
        if col not in df.columns:
            df[col] = "N/A"
    df = df[correct_columns]

    # Locate or insert row
    match = (df['School Year'] == year) & (df['BEIS School ID'] == school_id)
    if not match.any():
        new_row = {col: "N/A" for col in correct_columns}
        new_row["School Year"] = year
        new_row["BEIS School ID"] = school_id
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        row_idx = df.index[-1]
    else:
        row_idx = df[match].index[0]

    # Update the relevant column
    column_name = f"{grade} {gender}"
    if column_name not in df.columns:
        df[column_name] = "N/A"

    existing = df.at[row_idx, column_name]
    existing = 0 if pd.isna(existing) or existing == "N/A" else int(existing)
    df.at[row_idx, column_name] = existing + count

    df.to_csv(file_path, index=False, na_rep="N/A")

    return (
        f"Enrollment successfully updated for {school_name} ({grade}, {gender}) in {year}.",
        time.time()  # Returns a new number to trigger Store update
    )

@app.callback(
    Output('enrollment_table', 'data'),
    Output('enrollment_table', 'columns'),
    Input('table_school_year', 'value'),
    State('refresh_school_year_trigger', 'data')  # Get the store value too
)
def update_enrollment_table(school_year_from_dropdown, school_year_from_trigger):
    # Determine the effective school year
    school_year = school_year_from_dropdown or school_year_from_trigger or "2023-2024"

    file_path = f"data_files/data_{school_year}.csv"
    if not os.path.exists(file_path):
        return [], []

    df = pd.read_csv(file_path)

    # Inject Region and Division
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

if __name__ == "__main__":
    app.run(debug=True)