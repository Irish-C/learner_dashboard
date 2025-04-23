# layout/sidebar.py
# This module defines the sidebar layout for a Dash application.
from dash import html
from dash_iconify import DashIconify

def create_sidebar(is_collapsed=False, current_page=None):
    sidebar_style = {
        "position": "fixed",
        "top": "50px",
        "left": "0",
        "bottom": "0",
        "width": "180px" if not is_collapsed else "60px",
        "padding": "10px",
        "backgroundColor": "white",
        "boxShadow": "0px 0px 4px rgba(0, 0, 0, 0.1)",
        "overflowY": "auto",
        "transition": "width 0.3s ease",
        "textAlign": "left" if not is_collapsed else "center",
    }

    toggle_icon = DashIconify(
        icon="mdi:menu-open" if is_collapsed else "mdi:menu-close",
        width=24,
        style={"margin": "10px 0", "marginLeft": "5px"}
    )

    toggle_button = html.Button(
        html.Span(toggle_icon, style={"fontSize": "1.2rem"}),
        id='sidebar-toggle',
        className="sidebar-toggle-button"
    )

    # Define menu items with active state
    menu_items = html.Div([
        html.Button(
            [
                DashIconify(icon="mdi:view-dashboard", width=24),
                html.Span("Dashboard", className="navitem-text")
            ],
            id='btn-1',
            className="navitem" + (" active" if current_page == "dashboard" else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:database-edit", width=24),
                html.Span("EduData", className="navitem-text")
            ],
            id='btn-2',
            className="navitem" + (" active" if current_page == "manage_data" else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:help-circle-outline", width=24),
                html.Span("Help", className="navitem-text")
            ],
            id='btn-3',
            className="navitem" + (" active" if current_page == "help" else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:cog-outline", width=24),
                html.Span("Settings", className="navitem-text")
            ],
            id='btn-4',
            className="navitem" + (" active" if current_page == "settings" else ""),
        ),
    ])

    return html.Div(
        id='sidebar',
        className="sidebar",
        style=sidebar_style,
        children=[
            toggle_button,
            html.H4("Menu", className="chart-title", style={"textAlign": "left", "marginLeft": "10px", "marginBottom": "10px"} if not is_collapsed else {"display": "none"}),
            html.Hr(style={"borderColor": "var(--primary-color)", "borderWidth": "0.5px"} if not is_collapsed else {"display": "none"}),
            menu_items
        ]
    )