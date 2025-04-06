import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State

# Styles
def get_style(style_dict):
    return {**style_dict}

COMMON_TEXT_STYLE = {
    "fontWeight": "bold",
    "color": "#0a4485",
}

BODY_STYLE = get_style({
    "fontFamily": "'Segoe UI', Tahoma, sans-serif",
    "backgroundColor": "#f8f9fa",
    "margin": "0",
    "padding": "0",
})

HEADER_STYLE = get_style({
    "position": "fixed",
    "top": "0",
    "width": "100%",
    "background": "linear-gradient(90deg, #BFDBFE 0%, #DE082C 100%)",
    "height": "60px",
    "display": "flex",
    "alignItems": "center",
    "paddingLeft": "20px",
    "color": "#ffffff",
    "zIndex": "1000",
})

SIDEBAR_STYLE = get_style({
    "position": "fixed",
    "top": "60px",
    "left": "0",
    "bottom": "0",
    "padding": "10px",
    "backgroundColor": "white",
    "boxShadow": "0px 0px 4px rgba(0, 0, 0, 0.1)",
    "overflowY": "auto",
})

NAVITEM_SIDEBAR_TITLE_STYLE = get_style({
    "padding": "5px",
    "marginBottom": "5px",
    "cursor": "pointer",
    "color": "#0a4485",
    "fontWeight": "500",
    "display": "flex",
    "flexDirection": "column",
    "background": "none",
    "border": "none",
})

PLACEHOLDER_CARD_STYLE = get_style({
    "background": "#ffffff",
    "boxShadow": "0px 4px 4px rgba(0, 0, 0, 0.1)",
    "borderRadius": "8px",
    "padding": "20px",
    "textAlign": "center",
    "color": "#546778",
})

CHART_STYLE = get_style({
    "marginBottom": "15px",
    "fontSize": "1.2rem",
    **COMMON_TEXT_STYLE,
})

DEPED_LOGO = "https://1000logos.net/wp-content/uploads/2019/03/DepED-Logo.png"
PROFILE_PIC = "https://pbs.twimg.com/media/GX52I7TXUAAupJr.jpg"
USERNAME = "\u558a\u4e86\u4e2a\u51ac"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Learner Information System"


def create_header():
    return html.Div(
        style=HEADER_STYLE,
        children=[
            dbc.Container(
                dbc.Row([
                    dbc.Col(html.Img(src=DEPED_LOGO, height="40px"), width="auto", style={"paddingRight": "10px"}),
                    dbc.Col(dbc.NavbarBrand("Learners Information System",
                                            style={"fontFamily": "Helvetica",
                                                   "fontWeight": 700,
                                                   "fontSize": "1.25rem",
                                                   "background": "linear-gradient(180deg, #DE082C 0%, #0a4485 100%)",
                                                   "WebkitBackgroundClip": "text",
                                                   "WebkitTextFillColor": "transparent"}), width="auto"),
                    dbc.Col(width=True),
                    dbc.Col(html.Div([
                        html.Img(src=PROFILE_PIC, style={"borderRadius": "50%", "width": "40px", "height": "40px"}),
                        html.Span(USERNAME, style={"marginLeft": "8px", "color": "#ffffff", "whiteSpace": "nowrap"})
                    ], style={"display": "inline-flex", "alignItems": "center"}), width="auto")
                ], align="center", justify="between", className="g-0")
            )
        ]
    )


def create_sidebar(is_collapsed=False):
    toggle_button = html.Button(
        html.Span("\u2630" if is_collapsed else "\u2B9C", style={"fontSize": "1.2rem"}),
        id='sidebar-toggle',
        style={"background": "none", "border": "none", "color": "#0a4485", "cursor": "pointer",
               "marginBottom": "20px", "fontWeight": "bold", "textAlign": "left", "width": "100%"}
    )

    base_style = {
        **SIDEBAR_STYLE,
        "width": "60px" if is_collapsed else "220px",
        "textAlign": "center" if is_collapsed else "left",
        "transition": "width 0.3s ease"
    }

    if is_collapsed:
        return html.Div(id='sidebar', style=base_style, children=[toggle_button])
    else:
        return html.Div(id='sidebar', style=base_style, children=[
            toggle_button,
            html.H4("Menu", style={"marginTop": "10px", **COMMON_TEXT_STYLE, "fontSize": "1.2rem"}),
            html.Hr(style={"borderColor": "#0a4485", "borderWidth": "0.5px"}),
            html.Div([
                html.Button("Dashboard", id='btn-dashboard', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                html.Button("Enrollment", id='btn-enrollment', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                html.Button("Help", id='btn-help', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                html.Button("Settings", id='btn-settings', style=NAVITEM_SIDEBAR_TITLE_STYLE),
            ])
        ])


def create_placeholder_card(title, value):
    return html.Div(style=PLACEHOLDER_CARD_STYLE, children=[
        html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "10px", "fontWeight": "600"}),
        html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"})
    ])


def get_content_style(is_collapsed):
    return {
        "marginLeft": "60px" if is_collapsed else "220px",
        "marginTop": "60px",
        "padding": "20px",
        "minHeight": "calc(100vh - 60px)",
        "transition": "margin-left 0.3s ease"
    }


def create_content(page):
    if page == "dashboard":
        return html.Div(children=[
            html.H3("Dashboard", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
            html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
                             "gap": "20px", "marginTop": "20px"},
                     children=[
                         create_placeholder_card("Total Students", "0"),
                         create_placeholder_card("Active Students", "0"),
                         create_placeholder_card("New Enrollments", "0"),
                         create_placeholder_card("Number of Schools", "0"),
                     ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Analytics Overview", style=CHART_STYLE),
                html.Div("No data to display", style={**PLACEHOLDER_CARD_STYLE, "minHeight": "200px"}),
            ]),
            html.Div(style={"marginTop": "40px"}, children=[
                html.H4("Recent Activities", style=CHART_STYLE),
                html.Div("No recent activities to display", style={**PLACEHOLDER_CARD_STYLE, "minHeight": "200px"}),
            ])
        ])
    elif page == "enrollment":
        return html.Div(children=[
            html.H3("Enrollment Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
            html.Div("Content for Enrollment Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "help":
        return html.Div(children=[
            html.H3("Help Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
            html.Div("Content for Help Page goes here.", style={"fontSize": "1.2rem"})
        ])
    elif page == "settings":
        return html.Div(children=[
            html.H3("Settings Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
            html.Div("Content for Settings Page goes here.", style={"fontSize": "1.2rem"})
        ])


app.layout = html.Div(style=BODY_STYLE, children=[
    dcc.Store(id='current-page', data='dashboard'),
    dcc.Store(id='sidebar-collapsed', data=False),
    create_header(),
    html.Div(id='sidebar-container'),
    html.Div(id='content', children=create_content('dashboard')),
])


@app.callback(
    Output('sidebar-container', 'children'),
    Input('sidebar-collapsed', 'data'),
)
def update_sidebar_view(is_collapsed):
    return create_sidebar(is_collapsed)


@app.callback(
    Output('content', 'children'),
    Output('current-page', 'data'),
    Input('btn-dashboard', 'n_clicks'),  # Use the actual ID
    Input('btn-enrollment', 'n_clicks'), # Use the actual ID
    Input('btn-help', 'n_clicks'),       # Use the actual ID
    Input('btn-settings', 'n_clicks'),   # Use the actual ID
    State('current-page', 'data'),
)
def update_content(dashboard_clicks, enrollment_clicks, help_clicks, settings_clicks, current_page):
    ctx = callback_context
    if not ctx.triggered:
        return create_content(current_page), current_page

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-dashboard':
        return create_content('dashboard'), 'dashboard'
    elif button_id == 'btn-enrollment':
        return create_content('enrollment'), 'enrollment'
    elif button_id == 'btn-help':
        return create_content('help'), 'help'
    elif button_id == 'btn-settings':
        return create_content('settings'), 'settings'

@app.callback(
    Output('sidebar-collapsed', 'data'),
    Input('sidebar-toggle', 'n_clicks'),  # Use the actual ID
    State('sidebar-collapsed', 'data'),
    prevent_initial_call=True
)
def toggle_sidebar(n, is_collapsed):
    return not is_collapsed


@app.callback(
    Output('content', 'style'),
    Input('sidebar-collapsed', 'data')
)
def adjust_content_margin(is_collapsed):
    return get_content_style(is_collapsed)


if __name__ == "__main__":
    app.run(debug=True)
