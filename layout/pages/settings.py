from dash import html

def settings_content():
    return html.Div(children=[
        html.H1("Settings Page", className="page-title"),
        html.Div("Content for Settings Page goes here.", style={"fontSize": "1.2rem"})
    ])

print("Settings loaded...")