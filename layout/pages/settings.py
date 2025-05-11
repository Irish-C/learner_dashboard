from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Load user data CSV (assuming the CSV is at data_files/users.csv)
user_df = pd.read_csv("data_files/user-info.csv")

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

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
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
                    dbc.Button("Sign out",id="signout-btn", color="danger", className="w-100 mt-3")
                ], className="p-3 shadow-sm rounded bg-white")
            ], width=3),

            dbc.Col([
                html.H3("GENERAL SETTINGS", style={
                    "backgroundColor": "#1f4e79",
                    "color": "white",
                    "padding": "10px",
                    "borderRadius": "5px"
                }),
                dbc.Card([
                    dbc.CardHeader("About"),
                    dbc.CardBody([
                        html.P(user_data.get("about", "No bio available.")),
                    ])
                ], className="mb-3"),

                dbc.Card([
                    dbc.CardHeader("Basic Information"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(dbc.Input(placeholder="First name", value=first_name, disabled=True), width=6),
                            dbc.Col(dbc.Input(placeholder="Last name", value=last_name, disabled=True), width=6),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col(dbc.Input(placeholder="Username", value=user_data["username"], disabled=True), width=6),
                            dbc.Col(dbc.Input(placeholder="Phone number", value=user_data.get("contact", ""), disabled=True), width=6),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(placeholder="Email", value=user_data.get("Email", "")),
                            ], width=9),
                            dbc.Col([
                                dbc.Button("Update",id="update-email-btn", color="danger", className="w-100")
                            ], width=3)
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(placeholder="Password", type="password", value=user_data.get("Password","")),
                            ], width=9),
                            dbc.Col([
                                dbc.Button("Update", id="update-password-btn",color="danger", className="w-100")
                            ], width=3)
                        ])
                    ])
                ])
            ], width=9)
        ])
    ], className="p-4")
