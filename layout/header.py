from dash import html
import dash_bootstrap_components as dbc
from layout import temp_constants  # Import directly from the current package

def create_header():
    return html.Div(
        className="header",
        children=[
            dbc.Container(
                dbc.Row(
                    [
                        # DepEd Logo
                        dbc.Col(
                            html.Img(src=temp_constants.DEPED_LOGO, height="90px"),
                            width="auto",
                            className="d-flex align-items-center",
                            style={'paddingTop': '10px'}
                        ),

                        # Title and subtitle
                        dbc.Col(
                            html.Div(
                                [
                                    html.H4(
                                        "Learner Information System",
                                        className="header-brand",
                                        style={
                                            "paddingTop": "10px",
                                            "marginBottom": "0",
                                            "lineHeight": "0.75em",
                                        }

                                    ),
                                    html.Small(
                                        "Department of Education",
                                        className="text-muted",
                                        style={
                                            "fontSize": "12px",
                                            "marginTop": "0",
                                            "paddingTop": "0",
                                            "color": "blue", 
                                        }
                                    ),
                                ],
                                style={"marginLeft": "15px"},
                            ),
                            width="auto",
                            className="d-flex flex-column justify-content-center"
                        ),

                        # Spacer
                        dbc.Col(),

                        #Dynamic Profile section
                        dbc.Col(
                            dbc.DropdownMenu(
                                label=html.Span([
                                    html.Img(
                                        src="/assets/avatars/default.jpg",
                                        id="user-avatar",
                                        style={
                                            "height": "35px",
                                            "width": "35px",
                                            "borderRadius": "50%",
                                        }
                                    ),
                                    html.Span("username", id="user-name", style={
                                        "color": "white",
                                        "fontWeight": "bold",
                                    })
                                ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
                                children=[
                                    dbc.DropdownMenuItem("Settings", id="dropdown-settings"),
                                    dbc.DropdownMenuItem("Sign out", id="dropdown-logout")
                                ],
                                toggle_style={"backgroundColor": "transparent", "border": "none"}
                            ),
                            width="auto",
                            className="d-flex align-items-center justify-content-end pe-3 pt-4"
                        )
                    ],
                    align="center",
                    className="g-2"
                ),
                fluid=True
            )
        ]
    )