from dash import html

def manage_data_content():
    return html.Div(children=[
        html.H1("Manage Data Page", className="page-title"),
        html.Div("Content for Manage Data Page goes here.", style={"fontSize": "1.2rem"})
    ])

print("Manage Data loaded...")