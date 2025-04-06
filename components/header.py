import dash
import dash_bootstrap_components as dbc
from dash import html

DEPED_LOGO = "https://1000logos.net/wp-content/uploads/2019/03/DepED-Logo.png"
PROFILE_PIC = "https://pbs.twimg.com/media/GX52I7TXUAAupJr.jpg"
USERNAME = "Admin 3"

def create_header():
    return html.Div(
        className="header",
        children=[
            dbc.Container(
                dbc.Row([
                    dbc.Col(html.Img(src=DEPED_LOGO, height="40px"), width="auto", className="pe-2"),
                    dbc.Col(dbc.NavbarBrand("Learners Information System",
                                            style={"fontFamily": "Helvetica",
                                                   "fontWeight": 700,
                                                   "fontSize": "1.25rem",
                                                   "background": "linear-gradient(180deg, #DE082C 0%, #0a4485 100%)",
                                                   "WebkitBackgroundClip": "text",
                                                   "WebkitTextFillColor": "transparent"}), width="auto"),
                    dbc.Col(width=True),
                    dbc.Col(html.Div([
                        html.Img(src=PROFILE_PIC, style={"borderRadius": "50%", "width": "40px", "height": "40px"}),
                        html.Span(USERNAME, className="ms-2 text-white")
                    ], className="d-inline-flex align-items-center"), width="auto")
                ], align="center", justify="between", className="g-0")
            )
        ]
    )

if __name__ == '__main__':
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '../assets/style.css'])
    app.layout = create_header()
    app.run(debug=True)