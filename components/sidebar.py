from dash import html

def create_sidebar(is_collapsed=False):
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

    toggle_icon = html.Span("\u2630", style={"marginTop": "0px", "marginBottom": "50px"}) if is_collapsed else html.Span("\u00AB", style={"marginTop": "50px"})

    toggle_button = html.Button(
        html.Span(toggle_icon, style={"fontSize": "1.2rem"}),
        id='sidebar-toggle',
        className="sidebar-toggle-button"
    )

    menu_items = html.Div([
        html.Button(
            [html.I(className="fas fa-columns"), html.Span("Dashboard", className="navitem-text")],
            id='btn-1',
            className="navitem",
        ),
        html.Button(
            [html.I(className="fas fa-user-plus"), html.Span("Analytics", className="navitem-text")],
            id='btn-2',
            className="navitem",
        ),
        html.Button(
            [html.I(className="fas fa-question-circle"), html.Span("Help", className="navitem-text")],
            id='btn-3',
            className="navitem",
        ),
        html.Button(
            [html.I(className="fas fa-cog"), html.Span("Settings", className="navitem-text")],
            id='btn-4',
            className="navitem",
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