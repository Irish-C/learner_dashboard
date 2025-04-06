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
    dcc.Location(id='url', refresh=False, pathname='/dashboard'),
    dcc.Store(id='current-page', data='dashboard'),
    dcc.Store(id='sidebar-collapsed', data=False),
    html.Div(className="body-style", children=[
        header.create_header(),
        html.Div(className="app-container", children=[
            html.Div(id='sidebar-container'),
            html.Div(id='content'),
        ])
    ])
])

@app.callback(Output('sidebar-container', 'children'), Input('sidebar-collapsed', 'data'))
def update_sidebar_view(is_collapsed):
    return sidebar.create_sidebar(is_collapsed)

@app.callback(Output('content', 'children'), Output('current-page', 'data'), Input('url', 'pathname'), State('current-page', 'data'))
def update_content(pathname, current_page):
    page = pathname.lstrip('/')
    if page in ['dashboard', 'enrollment', 'help', 'settings']:
        return content.create_content(page), page
    return content.create_content(current_page), current_page

@app.callback(Output('sidebar-collapsed', 'data'), Input('sidebar-toggle', 'n_clicks'), State('sidebar-collapsed', 'data'), prevent_initial_call=True)
def toggle_sidebar(n, is_collapsed):
    return not is_collapsed

@app.callback(Output('content', 'style'), Input('sidebar-collapsed', 'data'), prevent_initial_call=False)
def adjust_content_margin(is_collapsed):
    return content.get_content_style(is_collapsed)

# Callback to update active link in the sidebar (more dynamic)
@app.callback(
    [Output(f'btn-{i}', 'className') for i in ['dashboard', 'enrollment', 'help', 'settings']],
    Input('url', 'pathname'),
    [State(f'btn-{i}', 'className') for i in ['dashboard', 'enrollment', 'help', 'settings']]
)
def update_active_link(pathname, *current_classes):
    active_class = "navitem active"
    inactive_class = "navitem"
    links = {'/': 'dashboard', '/dashboard': 'dashboard', '/enrollment': 'enrollment', '/help': 'help', '/settings': 'settings'}
    active_button = links.get(pathname, 'dashboard')

    updated_classes = []
    for i, class_name in enumerate(['dashboard', 'enrollment', 'help', 'settings']):
        updated_classes.append(active_class if class_name == active_button else inactive_class)
    return updated_classes

# Navigation callback (more concise)
@app.callback(Output('url', 'pathname'),
              [Input(f'btn-{i}', 'n_clicks') for i in ['dashboard', 'enrollment', 'help', 'settings']],
              State('url', 'pathname'), prevent_initial_call=True)
def navigate(*args):
    ctx = callback_context
    if ctx.triggered:
        return f"/{ctx.triggered[0]['prop_id'].split('-')[1]}"
    return dash.no_update

if __name__ == "__main__":
    app.run(debug=True)