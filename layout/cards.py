from dash import html

def create_placeholder_card(title, value):
    return html.Div(className="metric-card", children=[
        html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "10px", "fontWeight": "600"}),
        html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"})
    ])
def create_metric_card(title, value, icon):
    return html.Div(className="metric-card-style", children=[
        html.Div(className="metric-icon", children=[
            html.Img(src=icon, style={"width": "30px", "height": "30px"})
        ]),
        html.Div(className="metric-text", children=[
            html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "10px", "fontWeight": "600"}),
            html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"})
        ])
    ])