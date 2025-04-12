# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from dash import html
from ..cards import create_placeholder_card
from .. import temp_constants

def dashboard_content():
    return html.Div(children=[
        html.H1("Dashboard", className="page-title"),
        html.P(f"Welcome Back, {temp_constants.USERNAME}!", className="subtitle"),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))", "gap": "20px"},
            children=[
                create_placeholder_card("Total Students", "0"),
                create_placeholder_card("Active Students", "0"),
                create_placeholder_card("New Enrollments", "0"),
                create_placeholder_card("Number of Schools", "0"),
            ]
        ),
        html.Div(style={"marginTop": "40px"}, children=[
            html.H4("Analytics Overview", className="chart-title"),
            html.Div("No data to display", className="card", style={"minHeight": "200px"}),
        ]),
        html.Div(style={"marginTop": "40px"}, children=[
            html.H4("Recent Activities", className="chart-title"),
            html.Div("No recent activities to display", className="card", style={"minHeight": "200px"}),
        ])
    ])

print("dashboard_content loaded")