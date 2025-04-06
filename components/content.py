from dash import html
from .cards import create_placeholder_card

def get_content_style(is_collapsed):
    margin_left = "220px" if not is_collapsed else "60px"
    return {
        "marginLeft": margin_left,
        "marginTop": "60px",
        "padding": "20px",
        "minHeight": "calc(100vh - 60px)",
        "transition": "margin-left 0.3s ease", # Add transition for smooth animation
    }


def create_content(page):
    if page == "dashboard":
        return html.Div(children=[
            html.H3("Dashboard", className="common-text-style", style={"marginTop": "20px"}),
            html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
                             "gap": "20px", "marginTop": "20px"},
                     children=[
                         create_placeholder_card("Total Students", "0"),
                         create_placeholder_card("Active Students", "0"),
                         create_placeholder_card("New Enrollments", "0"),
                         create_placeholder_card("Number of Schools", "0"),
                     ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Analytics Overview", className="chart-style"),
                html.Div("No data to display", className="placeholder-card-style", style={"minHeight": "200px"}),
            ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Recent Activities", className="chart-style"),
                html.Div("No recent activities to display", className="placeholder-card-style", style={"minHeight": "200px"}),
            ])
        ])
    elif page == "enrollment":
        return html.Div(children=[
            html.H3("Enrollment Page", className="common-text-style", style={"marginTop": "20px"}),
            html.Div("Content for Enrollment Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "help":
        return html.Div(children=[
            html.H3("Help Page", className="common-text-style", style={"marginTop": "20px"}),
            html.Div("Content for Help Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "settings":
        return html.Div(children=[
            html.H3("Settings Page", className="common-text-style", style={"marginTop": "20px"}),
            html.Div("Content for Settings Page goes here.", style={"fontSize": "1.2rem"})
        ])
    return html.Div("Page not found")