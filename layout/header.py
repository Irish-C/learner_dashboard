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
                        dbc.Col(
                            html.Img(src=temp_constants.DEPED_LOGO, height="40px"),
                            width="auto",
                            className="d-flex align-items-center",
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("Learners Information System", className="header-brand", style={"marginLeft": "15px"}),
                            width="auto",
                            className="d-flex align-items-center",
                        ),
                        dbc.Col(width=True),  # Pushes the profile to the right
                        dbc.Col(
                            html.Div(
                                [
                                    html.Img(src=temp_constants.PROFILE_PIC, className="profile-pic"),
                                    html.Span(temp_constants.USERNAME, className="profile-name"),
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