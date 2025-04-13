from dash import html
from dash_iconify import DashIconify

def create_placeholder_card(title, value):
    return html.Div(className="placeholder-card-style", children=[
        html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "15px", "fontWeight": "600"}),  # Increased marginBottom
        html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"})
    ])

def create_metric_card(title, value="0", icon="mdi:chart-line", color="primary", delta=None):
    return html.Div(
        className="card kpi-card shadow-sm",
        style={
            "borderLeft": f"6px solid var(--bs-{color})",
            "borderRadius": "12px",
            "padding": "1.5rem",  # Increased padding for more spacing inside the card
            "backgroundColor": "white",
            "minHeight": "150px",  # Increased minimum height for more vertical space
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "transition": "all 0.3s ease",
            "marginBottom": "20px",  # Add spacing between cards
        },
        children=[
            html.Div([
                DashIconify(icon=icon, width=26, style={"color": f"var(--bs-{color})", "marginBottom": "15px"}),  # Increased marginBottom
                html.H5(title, style={"fontSize": "1.2rem", "margin": 0, "color": "#555", "marginBottom": "15px"}),  # Increased marginBottom
            ]),
            html.Div([
                html.H2(value, style={"margin": "0", "fontWeight": "bold", "color": "#222", "marginBottom": "10px"}),  # Increased marginBottom
                html.Span(delta, style={"fontSize": "0.85rem", "color": "#28a745"}) if delta else None
            ])
        ]
    )