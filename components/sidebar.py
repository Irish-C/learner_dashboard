from dash import html

def create_sidebar(is_collapsed=False):
    sidebar_style = {
        "position": "fixed",
        "top": "60px",
        "left": "0",
        "bottom": "0",
        "width": "220px" if not is_collapsed else "60px",
        "padding": "10px",
        "backgroundColor": "white",
        "boxShadow": "0px 0px 4px rgba(0, 0, 0, 0.1)",
        "overflowY": "auto",
        "transition": "width 0.3s ease",
        "textAlign": "left" if not is_collapsed else "center",
    }

    toggle_button = html.Button(
        html.Span("\u2630" if is_collapsed else "\u2B9C", style={"fontSize": "1.2rem"}),
        id='sidebar-toggle',
        className="navitem"
    )

    menu_items = html.Div([
        html.Button(
            "Dashboard" if not is_collapsed else html.I(className="fas fa-home"),
            id='btn-dashboard',
            className="navitem"
        ),
        html.Button(
            "Enrollment" if not is_collapsed else html.I(className="fas fa-user-plus"),
            id='btn-enrollment',
            className="navitem"
        ),
        html.Button(
            "Help" if not is_collapsed else html.I(className="fas fa-question-circle"),
            id='btn-help',
            className="navitem"
        ),
        html.Button(
            "Settings" if not is_collapsed else html.I(className="fas fa-cog"),
            id='btn-settings',
            className="navitem"
        ),
    ])

    return html.Div(
        id='sidebar',
        className="sidebar",
        style=sidebar_style,
        children=[
            toggle_button,
            html.H4("Menu", className="chart-title", style={"textAlign": "center", "marginBottom": "10px"} if is_collapsed else {"marginBottom": "10px"}),
            html.Hr(style={"borderColor": "var(--primary-color)", "borderWidth": "0.5px"} if not is_collapsed else {"display": "none"}),
            menu_items
        ]
    )