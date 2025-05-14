from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import dash
import os
import hashlib

# Load user data CSV
user_df = pd.read_csv("data_files/user-info.csv")

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def settings_content(current_user):
    try:
        first, last = current_user.strip().split()
        user_data = user_df[ 
            (user_df['First_Name'].str.lower() == first.lower()) & 
            (user_df['Last_Name'].str.lower() == last.lower()) 
        ]
        if user_data.empty:
            return html.Div("User not found in records.", style={"color": "red", "padding": "20px"})
        user_data = user_data.iloc[0]
    except Exception as e:
        return html.Div(f"Error loading user data: {str(e)}", style={"color": "red", "padding": "20px"})

    first_name = user_data['First_Name']
    last_name = user_data['Last_Name']
    avatar_path = f"/assets/avatars/{user_data['avatar']}" if pd.notna(user_data['avatar']) and os.path.isfile(f"assets/avatars/{user_data['avatar']}") else "/assets/avatars/default.jpg"

    # Content for tabs
    profile_settings_content = html.Div([
        dbc.Row([
            dbc.Col([html.Div([
                html.H6("User Profile", className="text-center text-secondary mb-2"),
                html.H5(f"{first_name} {last_name}", style={"fontWeight": "bold", "textAlign": "center"}),
                html.P(f"{user_data['username']}", style={"textAlign": "center", "color": "gray"}),
                html.Img(
                    src=avatar_path,
                    style={
                        "width": "100px",
                        "height": "100px",
                        "borderRadius": "50%",
                        "margin": "0 auto",
                        "display": "block"
                    },
                    id="user-avatar-img"
                ),
                dcc.Upload(
                    id="upload-photo",
                    children=dbc.Button("Upload New Photo", color="primary", className="w-100 mt-3"),
                    accept="image/*"
                ),
                html.P(f"Member since: {user_data['member_since']}", style={"textAlign": "center", "marginTop": "10px"}),
                html.P(user_data['department'], style={"textAlign": "center", "color": "#d9534f", "fontStyle": "italic"}),
                dbc.Button("Sign out", id="signout-btn", color="danger", className="w-100 mt-3")
            ], className="p-3 shadow-sm rounded bg-white")], width=3),

            dbc.Col([html.H3("PROFILE SETTINGS", style={
                "backgroundColor": "#1f4e79", "color": "white", "padding": "10px", "borderRadius": "5px"
            }),
            dbc.Card([
                dbc.CardHeader("About"),
                dbc.CardBody([
                    dbc.Textarea(
                        placeholder="Tell us about yourself...",
                        value=user_data.get("about", "No bio available."),
                        id="about-input",
                        style={"height": "100px"}
                    ),
                    dbc.Button("Update About", id="update-about-btn", color="danger", className="mt-2")
                ])
            ], className="mb-3"),

            dbc.Card([
                dbc.CardHeader("Basic Information"),
                dbc.CardBody([
                    dbc.Row([dbc.Col([dbc.Label("First Name"), dbc.Input(placeholder="First name", value=first_name, disabled=True)], width=6),
                            dbc.Col([dbc.Label("Last Name"), dbc.Input(placeholder="Last name", value=last_name, disabled=True)], width=6)], className="mb-2"),

                    dbc.Row([dbc.Col([dbc.Label("Username"), dbc.Input(placeholder="Username", value=user_data["username"], disabled=True)], width=6),
                            dbc.Col([dbc.Label("Contact Number"), dbc.Input(placeholder="Phone number", value=user_data.get("contact", ""), disabled=True)], width=6)], className="mb-2"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(placeholder="Email", value=user_data.get("Email", ""), disabled=True)
                            ], width=12),
                        ], className="mb-2"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Password"),
                                html.Div([
                                    dbc.Input(
                                        id={"type": "password-field", "index": "settings-current"},
                                        placeholder="Current Password",
                                        type="password",
                                        disabled=True,
                                        value=user_data.get("Password", "")
                                    ),
                                    html.I(
                                        className="fas fa-eye",
                                        id={"type": "password-toggle", "index": "settings-current"},
                                        n_clicks=0,
                                        style={
                                            "position": "absolute",
                                            "right": "15px",
                                            "top": "50%",
                                            "transform": "translateY(-50%)",
                                            "cursor": "pointer",
                                            "color": "#6c757d"
                                        }
                                    )
                                ], style={"position": "relative"})
                            ], width=12),
                        ], className="mb-2"),
                    ])
                ])
            ], width=9)
        ])
    ], className="p-4")

    # General Settings content
    general_settings_content = html.Div([
        html.H3("GENERAL SETTINGS", style={"backgroundColor": "#1f4e79", "color": "white", "padding": "10px", "borderRadius": "5px"}),
        html.P("This section is under construction.", style={"textAlign": "center"})
        # Add more content related to profile settings here
    ])
    # Theme Settings content
    theme_settings_content = html.Div([
        html.H3("THEMES", style={"backgroundColor": "#1f4e79", "color": "white", "padding": "10px", "borderRadius": "5px"}),
        html.P("Updates coming Soon! Stay tuned.", style={"textAlign": "center"})
        # Add more content related to profile settings here

    ])

    # Define common styles for the tabs
    tab_style = {
        'backgroundColor': '#f8f9fa',
        'color': '#1f4e79',
        'padding': '10px',
        'borderTopLeftRadius': '11px',
        'borderTopRightRadius': '11px'
    }

    tab_selected_style = {
        'backgroundColor': 'white',
        'color': '#1f4e79',
        'fontWeight': 'bold',
        'borderTopLeftRadius': '11px',
        'borderTopRightRadius': '11px'
    }

    # Tab structure
    return html.Div([
        dcc.Tabs([
            dcc.Tab(label='PROFILE', children=[profile_settings_content], style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='GENERAL', children=[general_settings_content], style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='THEMES', children=[theme_settings_content], style=tab_style, selected_style=tab_selected_style),
        ])
    ])