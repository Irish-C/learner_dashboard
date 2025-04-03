# Install Dependencies
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output

# Styles
def get_style(style_dict):
    return {**style_dict}

# Common styles
COMMON_TEXT_STYLE = {
    "fontWeight": "bold",
    "color": "#0a4485",
}

# Define styles for the application
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
    "width": "220px",
    "padding": "10px",
    "backgroundColor": "white",
    "boxShadow": "0px 0px 4px rgba(0, 0, 0, 0.1)",
    "overflowY": "auto",
})

CONTENT_STYLE = get_style({
    "marginLeft": "220px",
    "marginTop": "60px",
    "padding": "20px",
    "minHeight": "calc(100vh - 60px)",
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

# Constants
DEPED_LOGO = "https://1000logos.net/wp-content/uploads/2019/03/DepED-Logo.png"
PROFILE_PIC = "https://pbs.twimg.com/media/GX52I7TXUAAupJr.jpg"  # Admin profile picture URL
USERNAME = "咚了个冬"

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Learner Information System"

# Header component
def create_header():
  """Creates the header of the application."""
  return html.Div(
        style=HEADER_STYLE,
        children=[
            dbc.Container(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=DEPED_LOGO, height="40px"), width="auto", style={"paddingRight": "10px"}),
                        dbc.Col(dbc.NavbarBrand("Learners Information System",
                                                style={  "fontFamily": "Helvetica",
                                                         "fontWeight": 700,
                                                         "fontSize": "1.25rem",
                                                         "background":"linear-gradient(180deg, #DE082C 0%, #0a4485 100%)",
                                                         "WebkitBackgroundClip": "text",
                                                         "WebkitTextFillColor": "transparent",
                                                         }), width="auto"),
                        dbc.Col(width=True),  # Pushes profile section to the right
                        dbc.Col(
                            html.Div(
                                [
                                    html.Img(src=PROFILE_PIC, style={"border": "px solid #DE082C", "borderRadius": "50%", "width": "40px", "height": "40px"}),
                                    html.Span(
                                        USERNAME,
                                        style={
                                            "marginLeft": "8px",
                                            "color": "#ffffff",
                                            "whiteSpace": "nowrap",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "inline-flex",  # Both elements stay in one line
                                    "alignItems": "center",  # Aligns vertically
                                },
                            ),
                            width="auto",
                        ),
                    ],
                    align="center",
                    justify="between",
                    className="g-0",
                ),
            )
        ]
    )

# Sidebar component
def create_sidebar():
  """Creates the sidebar navigation menu."""
  return html.Div(
        style=SIDEBAR_STYLE,
        children=[
            html.H4("Menu", style={"marginTop": "30px", **COMMON_TEXT_STYLE, "fontSize": "1.2rem"}),
            html.Hr(style={"borderColor": "#0a4485", "borderWidth": "0.5px"}),
            html.Div(
                children=[
                    html.Button("Dashboard", id='btn-dashboard', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                    html.Button("Enrollment", id='btn-enrollment', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                    html.Button("Help", id='btn-help', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                    html.Button("Settings", id='btn-settings', style=NAVITEM_SIDEBAR_TITLE_STYLE),
                ],
            ),
        ],
    )

# Placeholder card component
def create_placeholder_card(title, value):
    return html.Div(
        style=PLACEHOLDER_CARD_STYLE,
        children=[
            html.Div(title, style={"fontSize": "1.2rem", "marginBottom": "10px", "fontWeight": "600"}),
            html.Div(value, style={"fontSize": "2rem", "fontWeight": "bold"}),
        ],
    )

# Content component
def create_content(page):
  """Creates the main content area based on the selected page."""
  if page == "dashboard":
        return html.Div(
            style=CONTENT_STYLE,
            children=[
                html.H3("Dashboard", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
                        "gap": "20px",
                        "marginTop": "20px",
                    },
                    children=[
                        create_placeholder_card("Total Students", "0"),
                        create_placeholder_card("Active Students", "0"),
                        create_placeholder_card("New Enrollments", "0"),
                        create_placeholder_card("Number of Schools", "0"),
                    ],
                ),
                html.Div(
                    style={"marginTop": "40px"},
                    children=[
                        html.H4("Analytics Overview", style=CHART_STYLE),
                        html.Div(
                            "No data to display",
                            style={**PLACEHOLDER_CARD_STYLE, "minHeight": "200px"},
                        ),
                    ],
                ),
                html.Div(
                    style={"marginTop": "40px"},
                    children=[
                        html.H4("Recent Activities", style=CHART_STYLE),
                        html.Div(
                            "No recent activities to display",
                            style={**PLACEHOLDER_CARD_STYLE, "minHeight": "200px"},
                        ),
                    ],
                ),
            ],
        )
  elif page == "enrollment":
        return html.Div(
            style=CONTENT_STYLE,
            children=[
                html.H3("Enrollment Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
                html.Div("Content for Enrollment Page goes here.", style={"fontSize": "1.2rem"}),
            ],
        )
  elif page == "help":
        return html.Div(
            style=CONTENT_STYLE,
            children=[
                html.H3("Help Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
                html.Div("Content for Help Page goes here.", style={"fontSize": "1.2rem"}),
            ],
        )
  elif page == "settings":
        return html.Div(
            style=CONTENT_STYLE,
            children=[
                html.H3("Settings Page", style={**COMMON_TEXT_STYLE, "marginTop": "20px"}),
                html.Div("Content for Settings Page goes here.", style={"fontSize": "1.2rem"}),
            ],
        )

# App Layout
app.layout = html.Div(
    style=BODY_STYLE,
    children=[
        create_header(),
        create_sidebar(),
        dcc.Store(id='current-page', data='dashboard'),  # Store to keep track of the current page
        html.Div(id='content', children=create_content('dashboard')),  # Initial content
    ],
)

# Callback to update content based on button clicks
@app.callback(
    Output('content', 'children'),
    Output('current-page', 'data'),
    Input('btn-dashboard', 'n_clicks'),
    Input('btn-enrollment', 'n_clicks'),
    Input('btn-help', 'n_clicks'),
    Input('btn-settings', 'n_clicks'),
    Input('current-page', 'data'),
)
def update_content(dashboard_clicks, enrollment_clicks, help_clicks, settings_clicks, current_page):
  """Updates the content displayed based on the button clicked."""
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

# Run the app
if __name__ == "__main__":
    app.run(debug=True)