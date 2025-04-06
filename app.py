import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
from components import header, sidebar, content

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
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

app.title = "Learner Information System"

app.layout = html.Div(children=[
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
    Input('btn-dashboard', 'n_clicks'),
    Input('btn-enrollment', 'n_clicks'),
    Input('btn-help', 'n_clicks'),
    Input('btn-settings', 'n_clicks'),
    State('current-page', 'data'),
)
def update_content(dashboard_clicks, enrollment_clicks, help_clicks, settings_clicks, current_page):
    ctx = callback_context
    if not ctx.triggered:
        return content.create_content(current_page), current_page

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-dashboard':
        return content.create_content('dashboard'), 'dashboard'
    elif button_id == 'btn-enrollment':
        return content.create_content('enrollment'), 'enrollment'
    elif button_id == 'btn-help':
        return content.create_content('help'), 'help'
    elif button_id == 'btn-settings':
        return content.create_content('settings'), 'settings'

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

if __name__ == "__main__":
    app.run(debug=True)