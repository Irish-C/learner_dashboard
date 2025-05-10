from dash import html
import dash_bootstrap_components as dbc

def settings_content():
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("IVAN D. PINILI", style={"fontWeight": "bold", "textAlign": "center"}),
                    html.P("@ibanny", style={"textAlign": "center", "color": "gray"}),
                    html.Img(
                        src="/assets/icons/ivan.jpg",
                        style={
                            "width": "100px",
                            "height": "100px",
                            "borderRadius": "50%",
                            "margin": "0 auto",
                            "display": "block"
                        }
                    ),
                    dbc.Button("Upload New Photo", color="primary", className="w-100 mt-3"),
                    html.P("Member since: 14 February 2024", style={"textAlign": "center", "marginTop": "10px"}),
                    html.P("NCR Dept.", style={"textAlign": "center", "color": "#d9534f", "fontStyle": "italic"}),
                    dbc.Button("Sign out", color="danger", className="w-100 mt-3")
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
                    dbc.CardBody([
                        html.H5("About"),
                        html.P("Listen to my new cover of Wiege!!"),
                        html.P("other songs: CURE, BLACK SORROW, MY CLEMANTIS (COVER)"),
                    ])
                ], className="mb-3"),

                dbc.Card([
                    dbc.CardBody([
                        html.H5("Basic Information"),
                        dbc.Row([
                            dbc.Col(dbc.Input(placeholder="Full name", value="Ivan", disabled=True), width=6),
                            dbc.Col(dbc.Input(placeholder="Last name", value="Pinili", disabled=True), width=6),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col(dbc.Input(placeholder="Username", value="@ibanny", disabled=True), width=6),
                            dbc.Col(dbc.Input(placeholder="Phone number", value="########", disabled=True), width=6),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(placeholder="Email", value="ivan@deped.com"),
                            ], width=9),
                            dbc.Col([
                                dbc.Button("Update", color="danger", className="w-100")
                            ], width=3)
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Input(placeholder="Password", type="password", value="*****"),
                            ], width=9),
                            dbc.Col([
                                dbc.Button("Update", color="danger", className="w-100")
                            ], width=3)
                        ])
                    ])
                ])
            ], width=9)
        ])
    ], className="p-4")
