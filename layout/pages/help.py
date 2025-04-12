from dash import html

def help_content():
    return html.Div(children=[
        html.H1("Help Page", className="page-title"),
        html.Div("Content for Help Page goes here.", style={"fontSize": "1.2rem"})
    ])

print("help_content loaded")