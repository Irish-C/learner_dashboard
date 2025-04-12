from dash import html

def enrollment_content():
    return html.Div(children=[
        html.H1("Enrollment Page", className="page-title"),
        html.Div("Content for Enrollment Page goes here.", style={"fontSize": "1.2rem"})
    ])

print("Enrollment Page loading...")