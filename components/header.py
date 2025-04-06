from dash import html
import dash_bootstrap_components as dbc

DEPED_LOGO = "https://1000logos.net/wp-content/uploads/2019/03/DepED-Logo.png"
PROFILE_PIC = "https://pbs.twimg.com/media/GX52I7TXUAAupJr.jpg"
USERNAME = "Admin 3"

def create_header():
    return html.Div(
        className="header",
        children=[
            dbc.Container(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=DEPED_LOGO, height="40px"),
                            width="auto",
                            className="d-flex align-items-center",
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("Learners Information System", className="header-brand", style={"marginLeft": "10px"}),
                            width="auto",
                            className="d-flex align-items-center",
                        ),
                        dbc.Col(width=True),  # Pushes the profile to the right
                        dbc.Col(
                            html.Div(
                                [
                                    html.Img(src=PROFILE_PIC, className="profile-pic"),
                                    html.Span(USERNAME, className="profile-name"),
                                ],
                                className="header-profile",
                            ),
                            width="auto",
                            className="d-flex align-items-center justify-content-end",
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
                fluid=True,  # Allows container to span the full width
            )
        ]
    )