import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State

from components import header, sidebar, content

# Mapping of numeric values to page names
PAGE_CONSTANTS = {
    1: 'dashboard',
    2: 'enrollment',
    3: 'help',
    4: 'settings'
}

# Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}],
    assets_folder='assets',
    suppress_callback_exceptions=True,
    title="Learner Information System"
)

# Load index template from the HTML file
with open('assets/index_template.html', 'r') as file:
    app.index_string = file.read()

# Layout with numeric constant for the default page (1 = 'dashboard')
app.layout = html.Div(children=[ 
    dcc.Location(id='url', refresh=False, pathname='/1'),  # Default page is '1' for Dashboard
    dcc.Store(id='current-page', data=1),  # Default page is '1' for Dashboard
    dcc.Store(id='sidebar-collapsed', data=False),
    html.Div(className="body-style", children=[ 
        header.create_header(),
        html.Div(className="app-container", children=[ 
            html.Div(id='sidebar-container'), 
            html.Div(id='content'),
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
    Input('url', 'pathname'),
    State('current-page', 'data'),
)
def update_content(pathname, current_page):
    page_num = int(pathname.lstrip('/'))  # Convert pathname to integer (e.g., '1' becomes 1)
    
    # Retrieve the page name from the numeric value
    page = PAGE_CONSTANTS.get(page_num, 'dashboard')  # Default to 'dashboard' if invalid page
    
    return content.create_content(page), page_num

@app.callback(
    Output('sidebar-collapsed', 'data'),
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar-collapsed', 'data'),
    prevent_initial_call=True
)
def toggle_sidebar(n, is_collapsed):
    if n is None:
        return is_collapsed
    return not is_collapsed

@app.callback(
    Output('content', 'style'),
    Input('sidebar-collapsed', 'data'),
    prevent_initial_call=False
)
def adjust_content_margin(is_collapsed):
    return content.get_content_style(is_collapsed)

# Callback to update active link in the sidebar (using numeric constants)
@app.callback(
    Output('btn-1', 'className'),  # Updated IDs to numeric constants
    Output('btn-2', 'className'),
    Output('btn-3', 'className'),
    Output('btn-4', 'className'),
    Input('url', 'pathname'),
    [State('btn-1', 'className'),
     State('btn-2', 'className'),
     State('btn-3', 'className'),
     State('btn-4', 'className')]
)
def update_active_link(pathname, class_dashboard, class_enrollment, class_help, class_settings):
    active_class = "navitem active"
    inactive_class = "navitem"
    
    # Get page number from pathname
    page_num = int(pathname.lstrip('/'))
    
    # Map numeric page value to actual page name
    if page_num == 1:
        return active_class, inactive_class, inactive_class, inactive_class
    elif page_num == 2:
        return inactive_class, active_class, inactive_class, inactive_class
    elif page_num == 3:
        return inactive_class, inactive_class, active_class, inactive_class
    elif page_num == 4:
        return inactive_class, inactive_class, inactive_class, active_class
    
    return inactive_class, inactive_class, inactive_class, inactive_class

# Navigation callback using numeric constants
@app.callback(
    Output('url', 'pathname'),
    Input('btn-1', 'n_clicks'),  # Updated button IDs
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks'),
    Input('btn-4', 'n_clicks'),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def navigate(n_dashboard, n_enrollment, n_help, n_settings, current_path):
    ctx = callback_context
    if not ctx.triggered:
        return current_path
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-1':  # Redirect to '1' (Dashboard)
            return f'/1'
        elif button_id == 'btn-2':  # Redirect to '2' (Enrollment)
            return f'/2'
        elif button_id == 'btn-3':  # Redirect to '3' (Help)
            return f'/3'
        elif button_id == 'btn-4':  # Redirect to '4' (Settings)
            return f'/4'
    return current_path

if __name__ == "__main__":
    app.run(debug=True)