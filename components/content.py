from dash import html
from .cards import create_placeholder_card

def get_content_style(is_collapsed):
    margin_left = "220px" if not is_collapsed else "60px"
    return {
        "marginLeft": margin_left,
        "marginTop": "60px",
        "padding": "20px",
        "minHeight": "calc(100vh - 60px)",
        "transition": "margin-left 0.3s ease",
    }

def create_content(page):
    if page == "dashboard":
        return html.Div(children=[
            html.H1("Dashboard", className="chart-title"),
            html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
                             "gap": "20px", "marginTop": "20px"},
                     children=[
                         create_placeholder_card("Total Students", "0"),
                         create_placeholder_card("Active Students", "0"),
                         create_placeholder_card("New Enrollments", "0"),
                         create_placeholder_card("Number of Schools", "0"),
                     ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Analytics Overview", className="chart-title"),
                html.Div("No data to display", className="card", style={"minHeight": "200px"}),
            ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Recent Activities", className="chart-title"),
                html.Div("No recent activities to display", className="card", style={"minHeight": "200px"}),
            ])
        ])
    elif page == "enrollment":
        return html.Div(children=[
            html.H1("Enrollment Page", className="chart-title", style={"marginTop": "20px"}),
            html.Div("Content for Enrollment Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "help":
        return html.Div(children=[
            html.H1("Help Page", className="chart-title", style={"marginTop": "20px"}),
            html.Div("Content for Help Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "settings":
        return html.Div(children=[
            html.H1("Settings Page", className="chart-title", style={"marginTop": "20px"}),
            html.Div("Content for Settings Page goes here.", style={"fontSize": "1.2rem"})
        ])
    return html.Div("Page not found")