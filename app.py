
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import re

from app_data import data, grade_columns, combined_shs_track_df, correct_region_order, grade_options

region_options = [{'label': r, 'value': r} for r in correct_region_order]

from layout import header, page_router, sidebar

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
    State('current-page', 'data')
)
def update_sidebar_view(is_collapsed, current_page):
    return sidebar.create_sidebar(is_collapsed, current_page)


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
    
    return page_router.create_content(
        page, 
        data, 
        grade_options, 
        region_options, 
        combined_shs_track_df
        ), page_num

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
    return page_router.get_content_style(is_collapsed)

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



# Dashboard Page
@app.callback(
    [Output('enrollment_bar_chart', 'figure'),
     Output('gender_pie_chart', 'figure'),
     Output('enrollment_vs_schools_chart', 'figure'),
     Output('kpi_card_row', 'children')],
    [Input('region_filter', 'value'),
     Input('grade_filter', 'value'),
     Input('gender_filter', 'value')]
)
def update_charts(selected_regions, selected_grades, selected_gender):
    print("update_charts triggered")
    filtered_data = data.copy()

    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    selected_grade_cols = []
    if selected_grades:
        for grade in selected_grades:
            if selected_gender == 'Male':
                selected_grade_cols += [col for col in data.columns if grade in col and 'Male' in col]
            elif selected_gender == 'Female':
                selected_grade_cols += [col for col in data.columns if grade in col and 'Female' in col]
            else:
                selected_grade_cols += [col for col in data.columns if grade in col]
        filtered_data['Selected Grades Total'] = filtered_data[selected_grade_cols].sum(axis=1)
    else:
        filtered_data['Selected Grades Total'] = filtered_data['Total Enrollment']

    if selected_gender == 'Male':
        filtered_data['Selected Grades Total'] = filtered_data[[col for col in grade_columns if 'Male' in col]].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Selected Grades Total'] = filtered_data[[col for col in grade_columns if 'Female' in col]].sum(axis=1)

    agg_data = filtered_data.groupby('Region')['Selected Grades Total'].sum().reset_index()

# Bar chart
    region_order_to_use = correct_region_order if agg_data['Region'].nunique() > 10 else None
    bar_chart = px.bar(
        agg_data,
        x='Region',
        y='Selected Grades Total',
        title='Enrollment Distribution by Region (Choropleth)',
        color='Region',
        text='Selected Grades Total',
        category_orders={'Region': region_order_to_use} if region_order_to_use else {}
    )

    bar_chart.update_layout(xaxis_title='Region', yaxis_title='Total Enrollment')

    # Pie Chart
    if selected_grades:
        selected_cols_male = [col for col in data.columns if any(g in col for g in selected_grades) and 'Male' in col]
        selected_cols_female = [col for col in data.columns if any(g in col for g in selected_grades) and 'Female' in col]
    else:
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]
    total_male = filtered_data[selected_cols_male].sum().sum()
    total_female = filtered_data[selected_cols_female].sum().sum()
    pie_chart = px.pie(
        names=['Male', 'Female'],
        values=[total_male, total_female],
        title='Gender Distribution',
        hole=0.6,
        color_discrete_sequence=['#b0cfff', '#f9c9e2']
    )

    # Filter by selected regions
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    # Determine relevant columns based on selected grades and gender
    selected_columns = []
    if selected_grades:
        for grade in selected_grades:
            if selected_gender == 'Male':
                selected_columns += [col for col in data.columns if grade in col and 'Male' in col]
            elif selected_gender == 'Female':
                selected_columns += [col for col in data.columns if grade in col and 'Female' in col]
            else:
                selected_columns += [col for col in data.columns if grade in col]
    else:
        if selected_gender == 'Male':
            selected_columns = [col for col in grade_columns if 'Male' in col]
        elif selected_gender == 'Female':
            selected_columns = [col for col in grade_columns if 'Female' in col]
        else:
            selected_columns = grade_columns

    # Calculate total enrollment based on selected columns
    filtered_data['Selected Grades Total'] = filtered_data[selected_columns].sum(axis=1)

    # Group by Division and Region
    agg_division = filtered_data.groupby(['Division', 'Region']).agg({
        'BEIS School ID': 'count',
        'Selected Grades Total': 'sum'
    }).rename(columns={'BEIS School ID': 'Number of Schools'}).reset_index()

    # Sort and select top 15 divisions
    agg_division = agg_division.sort_values(by='Selected Grades Total', ascending=False).head(15)

    # Create the figure
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(go.Bar(
        x=agg_division['Division'],
        y=agg_division['Selected Grades Total'],
        name='Total Enrollment'
    ), secondary_y=False)

    fig_combo.add_trace(go.Scatter(
        x=agg_division['Division'],
        y=agg_division['Number of Schools'],
        name='Number of Schools',
        mode='lines+markers'
    ), secondary_y=True)

    fig_combo.update_layout(
        title='Top 15 Divisions: Total Enrollment and Number of Schools',
        xaxis_title='Division',
        yaxis_title='Total Enrollment'
    )

    # KPI Cards Layout with icons and styling improvements
    total_students = int(filtered_data['Selected Grades Total'].sum())
    total_schools = filtered_data['BEIS School ID'].nunique()
    most_enrolled_division = filtered_data.groupby('Division')['Selected Grades Total'].sum().idxmax()

    kpi_cards = dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-user-graduate", style={"fontSize": "30px", "color": "#007BFF", "marginRight": "10px"}),
                        html.H5("Total Learners", style={"color": "var(--gray-color)"}),
                        html.H2(f"{total_students:,}", style={"color": "var(--blue-color"}),
                    ])
                ]),
                color="light",  # Light background for the card
                style={"borderRadius": "10px", "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)"}
            ),
            width=4,
            style={"marginBottom": "15px"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-school", style={"fontSize": "30px", "color": "#007BFF", "marginRight": "10px"}),
                        html.H5("Total Schools", style={"color": "var(--gray-color)"}),
                        html.H2(f"{total_schools:,}", style={"color": "var(--blue-color"}),
                    ])
                ]),
                color="light",
                style={"borderRadius": "10px", "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)"}
            ),
            width=4,
            style={"marginBottom": "15px"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-users-cog", style={"fontSize": "30px", "color": "#007BFF", "marginRight": "10px"}),
                        html.H5("Most Enrolled Division", style={"color": "var(--gray-color)"}),
                        html.H2(f"{most_enrolled_division}", style={"color": "var(--blue-color"}),
                    ])
                ]),
                color="light",
                style={"borderRadius": "10px", "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)"}
            ),
            width=4,
            style={"marginBottom": "15px"}
        ),
    ], justify="center", align="start")
    return bar_chart, pie_chart, fig_combo, kpi_cards

# Dashboard Page
@app.callback(
    Output('school_modal', 'is_open'),
    Output('modal_school_name', 'children'),
    Output('modal_school_body', 'children'),
    Input('school_search', 'value'),
    Input('modal_close_btn', 'n_clicks'),
    State('school_modal', 'is_open')
)
def toggle_modal(school_id, close_click, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, "", ""

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'modal_close_btn':
        return False, "", ""
    
    if school_id:
        school = data[data['BEIS School ID'] == school_id].iloc[0]
        return True, school['School Name'], html.Div([
            html.P(f"Region: {school['Region']}"),
            html.P(f"Division: {school['Division']}"),
            html.P(f"Barangay: {school['Barangay']}"),
            html.P(f"Total Enrollment: {school['Total Enrollment']:,.0f}"),
            html.P(f"Male: {school['Total Male']:,.0f}"),
            html.P(f"Female: {school['Total Female']:,.0f}")
        ])
    
    return is_open, "", ""

@app.callback(
    Output('enrollment_table', 'data'),
    Input('school_year_filter', 'value')
)
def update_table(selected_year):
    filtered_data = data[data['School Year'] == selected_year]
    return filtered_data[['Region', 'Division', 'Total Male', 'Total Female', 'Total Enrollment']].to_dict('records')


@app.callback(
    Output('shs_track_bar_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_shs_track_chart(selected_year, selected_regions, selected_gender):
    df_filtered = combined_shs_track_df.copy()

    # 🧠 Filter by school year
    if selected_year:
        df_filtered = df_filtered[df_filtered['School Year'] == selected_year]

    # 🧠 Filter by region
    if selected_regions:
        df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]

    # 🧠 Filter by gender
    if selected_gender != 'All':
        df_filtered = df_filtered[df_filtered['Gender'] == selected_gender]

    # ✅ Final protection: prevent plotly from erroring on empty or malformed data
    if df_filtered.empty:
        return go.Figure().update_layout(
            title="No data available for the selected filters",
            xaxis_title='Total Enrollment',
            yaxis_title='Track'
        )

    # 🧾 Group the data
    grouped = df_filtered.groupby(['Track', 'Grade Level'], as_index=False)['Total Enrollment'].sum()

    # 🔐 Defensive: check again if grouped is empty
    if grouped.empty:
        return px.bar(title="No data to display")

    # 📊 Plot the chart safely
    try:
        fig = px.bar(
            grouped,
            x='Total Enrollment',
            y='Track',
            color='Grade Level',
            orientation='h',
            text='Total Enrollment',
            title='Enrollment Distribution by SHS Track (G11 and G12)'
        )
        fig.update_layout(xaxis_title='Total Enrollment', yaxis_title='Track')
        return fig
    except Exception as e:
        print("SHS Chart Rendering Error:", e)
        return px.bar(title="Error rendering SHS Track chart")
    
@app.callback(
    Output('school_search', 'options'),
    Input('school_search', 'search_value')
)
def update_school_options(search_value):
    if not search_value:
        # Show first 5 schools when nothing is typed
        sample = data[['BEIS School ID', 'School Name']].dropna().head(10)
    else:
        sample = data[
            data['School Name'].str.contains(search_value, case=False, na=False) |
            data['BEIS School ID'].astype(str).str.contains(search_value)
        ].head(20)

    return [
        {'label': f"{row['BEIS School ID']} - {row['School Name']}", 'value': row['BEIS School ID']}
        for _, row in sample.iterrows()
    ]

if __name__ == "__main__":
    app.run(debug=True)
