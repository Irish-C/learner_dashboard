import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from components import header, sidebar, content

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
    title="Learner Information System"
)

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),  # Add dcc.Location
    dcc.Store(id='current-page', data='dashboard'),
    dcc.Store(id='sidebar-collapsed', data=False),
    html.Div(className="body-style", children=[
        header.create_header(),
        html.Div(className="app-container", children=[
            html.Div(id='sidebar-container'),
            html.Div(id='content', children=content.create_content('dashboard')),
        ])
    ])
])

@app.callback(
    Output('sidebar-container', 'children'),
    Input('sidebar-collapsed', 'data'),
)
def update_sidebar_view(is_collapsed):
    return sidebar.create_sidebar(is_collapsed)

@app.callback(
    Output('content', 'children'),
    Output('current-page', 'data'),
    Input('url', 'pathname'),  # Use pathname as input
    State('current-page', 'data'),
)
def update_content(pathname, current_page):
    page = pathname.lstrip('/')
    if page in ['dashboard', 'enrollment', 'help', 'settings']:
        return content.create_content(page), page
    return content.create_content(current_page), current_page # Default to current page if path not recognized

@app.callback(
    Output('sidebar-collapsed', 'data'),
    Input('sidebar-toggle', 'n_clicks'),
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
    return content.get_content_style(is_collapsed)

# Callback to update active link in the sidebar
@app.callback(
    Output('btn-dashboard', 'className'),
    Output('btn-enrollment', 'className'),
    Output('btn-help', 'className'),
    Output('btn-settings', 'className'),
    Input('url', 'pathname'),
    [State('btn-dashboard', 'className'),
     State('btn-enrollment', 'className'),
     State('btn-help', 'className'),
     State('btn-settings', 'className')]
)
def update_active_link(pathname, class_dashboard, class_enrollment, class_help, class_settings):
    active_class = "navitem active"
    inactive_class = "navitem"

    if pathname == '/' or pathname == '/dashboard':
        return active_class, inactive_class, inactive_class, inactive_class
    elif pathname == '/enrollment':
        return inactive_class, active_class, inactive_class, inactive_class
    elif pathname == '/help':
        return inactive_class, inactive_class, active_class, inactive_class
    elif pathname == '/settings':
        return inactive_class, inactive_class, inactive_class, active_class
    return inactive_class, inactive_class, inactive_class, inactive_class

# Modify the existing content update callback to use dcc.Location
@app.callback(
    Output('url', 'pathname'),
    Input('btn-dashboard', 'n_clicks'),
    Input('btn-enrollment', 'n_clicks'),
    Input('btn-help', 'n_clicks'),
    Input('btn-settings', 'n_clicks'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def navigate(n_dashboard, n_enrollment, n_help, n_settings, current_path):
    ctx = callback_context
    if not ctx.triggered:
        return current_path
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-dashboard':
            return '/dashboard'
        elif button_id == 'btn-enrollment':
            return '/enrollment'
        elif button_id == 'btn-help':
            return '/help'
        elif button_id == 'btn-settings':
            return '/settings'
    return current_path

if __name__ == "__main__":
    app.run(debug=True)