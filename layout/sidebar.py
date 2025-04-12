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
        toggle_icon,
        id='sidebar-toggle',
        className="sidebar-toggle-button"
    )


    menu_items = html.Div([
        html.Button(
            [
                DashIconify(icon="mdi:view-dashboard", width=24),  # Rounded dashboard icon
                html.Span("Dashboard", className="navitem-text")
            ],
            id='btn-1',
            className="navitem" + (" active" if current_page == 1 else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:chart-areaspline", width=24),
                html.Span("Analytics", className="navitem-text")
            ],
            id='btn-2',
            className="navitem" + (" active" if current_page == 2 else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:help-circle-outline", width=24),
                html.Span("Help", className="navitem-text")
            ],
            id='btn-3',
            className="navitem" + (" active" if current_page == 3 else ""),
        ),
        html.Button(
            [
                DashIconify(icon="mdi:cogs", width=24),
                html.Span("Settings", className="navitem-text")
            ],
            id='btn-4',
            className="navitem" + (" active" if current_page == 4 else ""),
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