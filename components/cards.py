from dash import html

def create_placeholder_card(title, value):
    return html.Div(className="placeholder-card-style", children=[
        html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "10px", "fontWeight": "600"}),
        html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"})
    ])