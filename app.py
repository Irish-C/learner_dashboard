import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import re
import json
import os

from layout.sidebar import create_sidebar
from layout.header import create_header
from layout.page_router import get_content_style, create_content
from layout.cards import create_metric_card
from app_data import data, grade_columns, combined_shs_track_df, correct_region_order, grade_options, barangay_options, division_options, school_options

region_options = [{'label': r, 'value': r} for r in correct_region_order]

# Mapping of numeric values to page names
PAGE_CONSTANTS = {
    1: 'dashboard',
    2: 'manage_data',
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

# Define the layout
app.layout = html.Div(
    className="body-style",
    children=[
        # Store the sidebar toggle state
        dcc.Store(id='sidebar-toggle-state', data=False),
        
        # Store current page
        dcc.Store(id='current-page', data="dashboard"),
        
        # Header
        create_header(),
        
        # Main content area with sidebar and page content
        html.Div(
            className="app-container",
            children=[
                # Sidebar (wrapped in a div container for dynamic updates)
                html.Div(
                    id="sidebar-container",
                    children=[create_sidebar(is_collapsed=False, current_page="dashboard")]
                ),
                
                # Page content
                html.Div(
                    id="content",
                    style=get_content_style(False),
                    children=create_content("dashboard", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options)
                )
            ]
        )
    ]
)

# Callback to toggle sidebar
@app.callback(
    Output("sidebar-container", "children", allow_duplicate=True), 
    Output("content", "style"), 
    Output("sidebar-toggle-state", "data"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-toggle-state", "data"), 
    State("current-page", "data"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, is_collapsed, current_page):
    if n_clicks:
        is_collapsed = not is_collapsed
    
    # Update sidebar with new collapsed state and current page
    updated_sidebar = create_sidebar(is_collapsed=is_collapsed, current_page=current_page)
    
    # Update content margin
    content_style = get_content_style(is_collapsed)
    
    return [updated_sidebar], content_style, is_collapsed

# Callback to change pages
@app.callback(
    Output("content", "children"), 
    Output("current-page", "data"), 
    Output("sidebar-container", "children"),
    Input("btn-1", "n_clicks"),
    Input("btn-2", "n_clicks"),
    Input("btn-3", "n_clicks"),
    Input("btn-4", "n_clicks"),
    State("current-page", "data"), 
    State("sidebar-toggle-state", "data")
)
def change_page(btn1, btn2, btn3, btn4, current_page, is_collapsed):
    ctx = callback_context
    if not ctx.triggered:
        return create_content("dashboard", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "dashboard", create_sidebar(is_collapsed=is_collapsed, current_page="dashboard")
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-1":
        return create_content("dashboard", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "dashboard", create_sidebar(is_collapsed=is_collapsed, current_page="dashboard")
    elif button_id == "btn-2":
        return create_content("manage_data", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "manage_data", create_sidebar(is_collapsed=is_collapsed, current_page="manage_data")
    elif button_id == "btn-3":
        return create_content("help", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "help", create_sidebar(is_collapsed=is_collapsed, current_page="help")
    elif button_id == "btn-4":
        return create_content("settings", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "settings", create_sidebar(is_collapsed=is_collapsed, current_page="settings")
    
    # Default to dashboard
    return create_content("dashboard", data, grade_options, region_options, combined_shs_track_df, division_options, school_options, barangay_options), "dashboard", create_sidebar(is_collapsed=is_collapsed, current_page="dashboard")



# Dashboard Page
@app.callback(
    [Output('gender_pie_chart', 'figure'),
     Output('enrollment_vs_schools_chart', 'figure'),
     Output('kpi_card_row', 'children'),
     Output('most_enrolled_division_card', 'children')],
    [Input('region_filter', 'value'),
     Input('grade_filter', 'value'),
     Input('gender_filter', 'value')]
)
def update_charts(selected_regions, selected_grades, selected_gender):
    print("update_charts triggered")
    filtered_data = data.copy()

    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    selected_cols_male = []
    selected_cols_female = []

    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]

    # Apply gender filtering to the DataFrame
    filtered_data = data.copy()
    if selected_gender == 'Male':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

    # Pie Chart
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]
    total_male = filtered_data[selected_cols_male].sum().sum()
    total_female = filtered_data[selected_cols_female].sum().sum()
    pie_chart = px.pie(
        names=['Male', 'Female'],
        values=[total_male, total_female],
        title='Gender Distribution',
        hole=0.6,
        color_discrete_sequence=['#b0cfff', '#f9c9e2']
    )

    pie_chart.update_traces(textinfo='percent')

    pie_chart.update_layout(
        margin=dict(t=30, b=0, l=0, r=0),
        height=296,  # or adjust for your visual preference
        showlegend=True  # set to False if pie labels suffice
    )

    # Filter by selected regions
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]
    
    if selected_gender == 'Male':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Selected Grades Total'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

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

    # KPI Cards Layout
    # Aggregate stats
    total_students = int(filtered_data['Selected Grades Total'].sum())
    total_schools = filtered_data['BEIS School ID'].nunique()
    region_total = filtered_data.groupby('Region')['Selected Grades Total'].sum().max()

    # 🔓 Use full dataset to get the true most enrolled region (before filtering by selected_regions)
    full_region_data = data.copy()

    # Optional: filter by gender and grades, but NOT by region
    selected_cols = []
    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols += [col for col in full_region_data.columns if col.startswith(grade)]
            else:
                selected_cols += [f"{grade} Male", f"{grade} Female"]
    else:
        selected_cols = grade_columns

    if selected_gender == 'Male':
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols if 'Male' in col]].sum(axis=1)
    elif selected_gender == 'Female':
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols if 'Female' in col]].sum(axis=1)
    else:
        full_region_data['Selected Grades Total'] = full_region_data[[col for col in selected_cols]].sum(axis=1)

    # 🔍 Calculate most enrolled region regardless of region filter
    region_enrollment = full_region_data.groupby('Region')['Selected Grades Total'].sum()
    most_enrolled_region = region_enrollment.idxmax()
    region_total = region_enrollment.max()


    # KPI Cards (now with Region card inside the 3-col row)
    kpi_cards = dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-user-graduate", style={
                            "fontSize": "30px",
                            "color": "var(--green-color)",
                            "marginBottom": "10px",
                            "backgroundColor": "color: var(--accent-color)",
                        }),
                        html.H5("Total Enrolled", style={
                            "color": "var(--gray-color)",
                            "margin": "0",
                            "fontWeight": "bold"
                        }),
                        html.H2(f"{total_students:,}", style={
                            "color": "var(--green-color)",
                            "margin": "0"
                        })
                    ], style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "100%"
                    })
                ]),
                color="light",
                style={
                    "borderRadius": "10px",
                    "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                    "borderBottom": "5px solid #28a745",
                    "padding": "10px"
                }
            ),
            width=4, style={"marginBottom": "15px"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-school", style={
                            "fontSize": "30px",
                            "color": "var(--yellow-color)",
                            "marginBottom": "10px"
                        }),
                        html.H5("Total Schools", style={
                            "color": "var(--gray-color)",
                            "margin": "0",
                            "fontWeight": "bold"
                        }),
                        html.H2(f"{total_schools:,}", style={
                            "color": "var(--yellow-color)",
                            "margin": "0"
                        })
                    ], style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "100%"
                    })
                ]),
                color="light",
                style={
                    "borderRadius": "10px",
                    "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                    "borderBottom": "5px solid #ffc107",
                    "padding": "10px"
                }
            ),
            width=4, style={"marginBottom": "15px"}
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-map-marked-alt", style={
                            "fontSize": "35px",
                            "color": "#e74c3c",
                            "marginBottom": "10px"
                        }),
                        html.H5("Most Enrolled Region as of (school year)", style={
                            "color": "var(--gray-color)",
                            "margin": "0",
                            "fontWeight": "bold"

                        }),
                        html.H3(f"{most_enrolled_region}: {region_total/1000:.2f}k", style={
                            "color": "#e74c3c",
                            "margin": "0",
                        })
                    ], style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "100%"
                    })
                ]),
                color="light",
                style={
                    "borderRadius": "10px",
                    "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                    "borderBottom": "5px solid #e74c3c",
                    "padding": "10px"
                }
            ),
            width=4, style={"marginBottom": "15px"}
        )
    ], justify="center", align="start")


    # Standalone Most Enrolled Division Card
    most_enrolled_division_text = filtered_data.groupby('Division')['Selected Grades Total'].sum().idxmax()
    most_enrolled_division_card = html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-users-cog", style={
                        "fontSize": "30px",
                        "color": "#007BFF",
                        "marginBottom": "0.5rem"
                    }),
                    html.H5("Most Enrolled Division", style={
                        "color": "var(--gray-color)",
                        "textAlign": "center",
                        "margin": "0",
                        "lineHeight": "1.2"
                    }),
                    html.H2(f"{most_enrolled_division_text}", style={
                        "color": "var(--blue-color)",
                        "textAlign": "center",
                        "margin": "0"
                    })  # dynamic text
                ])
            ]),
            style={
                "borderRadius": "10px",
                "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",
                "width": "100%"  # ensure it fills its column
            }
        )
    ])


    return pie_chart, fig_combo, kpi_cards, most_enrolled_division_card


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


@app.callback(
    Output('top_schools_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_top_schools_chart(selected_regions, selected_grades, selected_gender):
    filtered_data = data.copy()
    if selected_regions:
        filtered_data = filtered_data[filtered_data['Region'].isin(selected_regions)]

    selected_cols_male = []
    selected_cols_female = []

    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]

    # Apply gender filtering to the DataFrame
    if selected_gender == 'Male':
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_female].sum(axis=1)
    else:
        filtered_data['Filtered Enrollment'] = filtered_data[selected_cols_male + selected_cols_female].sum(axis=1)

    # Top 5 schools by enrollment (regardless of sector)
    top_schools_df = (
        filtered_data.groupby(['School Name', 'Sector'], as_index=False)['Filtered Enrollment']
        .sum()
        .sort_values(by='Filtered Enrollment', ascending=False)
        .head(5)
    )

    # Color scheme
    colors = {
        'Public': '#3498db',
        'Private': '#e74c3c',
        'SUCsLUCs': '#f1c40f'
    }

    # Create sector-based traces
    fig = go.Figure()
    for sector in ['Public', 'Private', 'SUCsLUCs']:
        sector_data = top_schools_df[top_schools_df['Sector'] == sector]
        if not sector_data.empty:
            fig.add_trace(go.Bar(
                y=sector_data['School Name'],
                x=sector_data['Filtered Enrollment'],
                name=sector,
                orientation='h',
                marker=dict(color=colors.get(sector, '#7f8c8d')),
                text=sector_data['Filtered Enrollment'].map('{:,.0f}'.format),
                textposition='inside',
                hovertemplate='<b>%{y}</b><br>Enrollment: %{x:,}<extra></extra>'
            ))

    fig.update_layout(
        title='Top 5 Schools by Enrollment',
        barmode='stack',
        showlegend=True,
        legend_title_text='',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=40, t=60, b=60),
        xaxis=dict(title='Enrollment', gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(
            categoryorder='array',
            categoryarray=top_schools_df['School Name'].tolist()[::-1],
            title='',
            showgrid=False,
            automargin=True,
            ticklabelposition="outside left",
            tickfont=dict(size=13, family="Arial"),
            ticksuffix='  '
        ),

        font=dict(size=13),
        legend=dict(orientation='h', y=-0.25, x=0.5, xanchor='center')
    )
    return fig

@app.callback(
    Output('sned_sector_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_sned_sector_chart(selected_year, selected_regions, selected_gender):
    filtered_df = data.copy()

    if selected_year:
        filtered_df = filtered_df[filtered_df['School Year'] == selected_year]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

    # Select relevant columns for NG enrollment
    male_ng_cols = [col for col in filtered_df.columns if 'NG' in col and 'Male' in col]
    female_ng_cols = [col for col in filtered_df.columns if 'NG' in col and 'Female' in col]

    if selected_gender == 'Male':
        filtered_df['SNed'] = filtered_df[male_ng_cols].sum(axis=1)
        gender_cols = ['SNed']
        stack_name_map = {'SNed': 'Male'}
    elif selected_gender == 'Female':
        filtered_df['SNed'] = filtered_df[female_ng_cols].sum(axis=1)
        gender_cols = ['SNed']
        stack_name_map = {'SNed': 'Female'}
    else:
        filtered_df['SNed_Male'] = filtered_df[male_ng_cols].sum(axis=1)
        filtered_df['SNed_Female'] = filtered_df[female_ng_cols].sum(axis=1)
        gender_cols = ['SNed_Male', 'SNed_Female']
        stack_name_map = {'SNed_Male': 'Male', 'SNed_Female': 'Female'}

    # Group by sector and sum
    grouped = filtered_df.groupby('Sector')[gender_cols].sum().reset_index()
    melted = pd.melt(grouped, id_vars='Sector', var_name='Gender', value_name='Enrollment')
    melted['Gender'] = melted['Gender'].map(stack_name_map)

    fig = px.bar(
        melted,
        x='Sector',
        y='Enrollment',
        color='Gender',
        barmode='stack',
        text='Enrollment',
        title='SNed Enrollment by School Sector and Gender'
    )

    fig.update_layout(
        xaxis_title='School Sector',
        yaxis_title='Total Enrollment',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=13),
        legend_title_text='',
        margin=dict(l=20, r=20, t=50, b=40)
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='inside')
    return fig

@app.callback(
    Output('transition_rate_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_transition_rate_chart(selected_sy, selected_regions, selected_gender):
    df_sy_n = data[data['School Year'] == selected_sy]

    # Previous year setup (mocked)
    try:
        previous_sy = str(int(selected_sy.split('-')[0]) - 1) + '-' + str(int(selected_sy.split('-')[1]) - 1)
    except:
        previous_sy = "N/A"
    df_sy_n1 = data[data['School Year'] == previous_sy]

    if selected_regions:
        df_sy_n = df_sy_n[df_sy_n['Region'].isin(selected_regions)]
        df_sy_n1 = df_sy_n1[df_sy_n1['Region'].isin(selected_regions)]

    # Helper function
    def gender_filter(df, grade_base):
        if selected_gender == 'Male':
            cols = [f"{grade_base} Male"]
        elif selected_gender == 'Female':
            cols = [f"{grade_base} Female"]
        else:
            cols = [f"{grade_base} Male", f"{grade_base} Female"]
        return df[cols].sum().sum()

    # Placeholder logic if no prev year exists
    if df_sy_n1.empty:
        tr_elem_jhs = 0
        tr_jhs_shs = 0
    else:
        g6 = gender_filter(df_sy_n1, "G6")
        g7 = gender_filter(df_sy_n, "G7")
        tr_elem_jhs = (g7 / g6) * 100 if g6 else 0

        g10 = gender_filter(df_sy_n1, "G10")
        g11_cols = [col for col in df_sy_n.columns if "G11" in col and (selected_gender in col or selected_gender == 'All')]
        g11 = df_sy_n[g11_cols].sum().sum()
        tr_jhs_shs = (g11 / g10) * 100 if g10 else 0

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=tr_elem_jhs,
        domain={'x': [0, 0.5], 'y': [0, 1]},
        title={'text': "Elementary to JHS"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#1f77b4"}}
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=tr_jhs_shs,
        domain={'x': [0.5, 1], 'y': [0, 1]},
        title={'text': "JHS to SHS"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#ff7f0e"}}
    ))

    fig.update_layout(title="Transition Rates (Placeholder as there are no previous year)", height=300)
    return fig

@app.callback(
    Output('k_to_12_distribution_chart', 'figure'),
    Input('region_filter', 'value'),
    Input('gender_filter', 'value'),
    Input('school_year_filter', 'value')
)
def update_k_to_12_distribution(selected_regions, selected_gender, selected_year):
    filtered = data.copy()

    if selected_year:
        filtered = filtered[filtered['School Year'] == selected_year]
    if selected_regions:
        filtered = filtered[filtered['Region'].isin(selected_regions)]

    # Define grade groupings
    level_order = ['K', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'Elem NG',
                   'G7', 'G8', 'G9', 'G10', 'JHS NG', 'G11', 'G12']
    level_labels = {
        'K': 'Kinder', 'G1': 'Grade 1', 'G2': 'Grade 2', 'G3': 'Grade 3', 'G4': 'Grade 4',
        'G5': 'Grade 5', 'G6': 'Grade 6', 'Elem NG': 'NG-ES', 'G7': 'Grade 7',
        'G8': 'Grade 8', 'G9': 'Grade 9', 'G10': 'Grade 10', 'JHS NG': 'NG-JHS',
        'G11': 'Grade 11', 'G12': 'Grade 12'
    }

    level_group = {
        'K': 'ES', 'G1': 'ES', 'G2': 'ES', 'G3': 'ES', 'G4': 'ES', 'G5': 'ES', 'G6': 'ES', 'Elem NG': 'ES',
        'G7': 'JHS', 'G8': 'JHS', 'G9': 'JHS', 'G10': 'JHS', 'JHS NG': 'JHS',
        'G11': 'SHS', 'G12': 'SHS'
    }

    records = []
    for level in level_order:
        if level in ['G11', 'G12']:
            male_cols = [col for col in data.columns if col.startswith(level) and 'Male' in col]
            female_cols = [col for col in data.columns if col.startswith(level) and 'Female' in col]
        else:
            male_cols = [col for col in data.columns if col == f"{level} Male"]
            female_cols = [col for col in data.columns if col == f"{level} Female"]



        if selected_gender == 'Male':
            total = filtered[male_cols].sum().sum()
        elif selected_gender == 'Female':
            total = filtered[female_cols].sum().sum()
        else:
            total = filtered[male_cols + female_cols].sum().sum()

        records.append({
            'Level': level_labels[level],
            'Enrollment': total,
            'Group': level_group[level]
        })

    dist_df = pd.DataFrame(records)

    fig = px.bar(
        dist_df,
        x='Level',
        y='Enrollment',
        color='Group',
        category_orders={'Level': list(level_labels.values())},
        color_discrete_map={'ES': '#a3c4f3', 'JHS': '#2a6fdb', 'SHS': '#071952'},
        title='Enrollment Distribution Kinder to Grade 12 (include SNed)',
        text='Enrollment'
    )

    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker_line_width=0
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='Enrollment',
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center'),
        font=dict(size=13),
        bargap=0.2
    )

    return fig

with open('ph.json', 'r', encoding='utf-8') as file:
    geojson_data = json.load(file)

# Mapping of DataFrame regions to GeoJSON regions
region_mapping = {
    'BARMM': 'Autonomous Region in Muslim Mindanao',
    'CAR': 'Cordillera Administrative Region',
    'CARAGA': 'Caraga',
    'MIMAROPA': 'Mimaropa',
    'NCR': 'National Capital Region',
    'Region I': 'Ilocos',
    'Region II': 'Cagayan Valley',
    'Region III': 'Central Luzon',
    'Region IV-A': 'Calabarzon',
    'Region V': 'Bicol',
    'Region VI': 'Western Visayas',
    'Region VII': 'Central Visayas',
    'Region VIII': 'Eastern Visayas',
    'Region IX': 'Zamboanga Peninsula',
    'Region X': 'Northern Mindanao',
    'Region XI': 'Davao',
    'Region XII': 'Soccsksargen'
}

import plotly.graph_objects as go

@app.callback(
    Output('enrollment_choropleth_map', 'figure'),
    Input('region_filter', 'value')
)
def update_enrollment_choropleth(selected_regions):
    # 1) Copy + remap region names
    df_sy = data.copy()
    df_sy['Region'] = df_sy['Region'].apply(lambda x: region_mapping.get(x, x))

    # 2) Total enrollment for every region
    full_enrollment = (
        df_sy
        .groupby('Region', as_index=False)['Total Enrollment']
        .sum()
    )

    # 3) If a filter is applied, restrict to those regions; else use all
    if selected_regions:
        mapped = [region_mapping.get(r, r) for r in selected_regions]
        region_enrollment = full_enrollment[full_enrollment['Region'].isin(mapped)]
    else:
        region_enrollment = full_enrollment.copy()

    # 4) Build layered choropleth
    fig = go.Figure()

    # 4a) Base: all regions in light grey
    fig.add_choropleth(
        geojson=geojson_data,
        locations=full_enrollment['Region'],
        z=[0]*len(full_enrollment),            # dummy zeros
        featureidkey='properties.name',
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        showscale=False,
        marker_line_width=0.5,
        marker_line_color='white',
        hoverinfo='none'
    )

    # 4b) Overlay: colored for selected/all regions
    fig.add_choropleth(
        geojson=geojson_data,
        locations=region_enrollment['Region'],
        z=region_enrollment['Total Enrollment'],
        featureidkey='properties.name',
        colorbar_title="Total Enrollment",
        coloraxis="coloraxis"
    )

    # 5) Shared color axis and layout
    fig.update_layout(
        coloraxis=dict(
            colorscale="Viridis",
            cmin=full_enrollment['Total Enrollment'].min(),
            cmax=full_enrollment['Total Enrollment'].max()
        ),
        title="Total Enrollment by Region",
        geo=dict(fitbounds="locations", visible=False),
        margin={"r":0,"t":50,"l":0,"b":0},
        height=500
    )

    return fig

# Callback for updating Stacked bar chart of school offerings by COC
@app.callback(
    Output('coc_sector_chart', 'figure'),
    Input('school_year_filter', 'value'),
    Input('region_filter', 'value'),
    Input('grade_filter', 'value'),
    Input('gender_filter', 'value')
)
def update_coc_sector_chart(selected_sy, selected_regions, selected_grades, selected_gender):
    # Make a copy of the full dataset
    df = data.copy()

    # Filter Dataset by selected school year
    df = df[df['School Year'] == selected_sy]

    # Filter Dataset to inlcude only those regions
    if selected_regions:
        df = df[df['Region'].isin(selected_regions)]

    # Initialize empty lists 
    selected_cols_male = []
    selected_cols_female = []

    # Dynamically determine which columns to sum based on selected grades
    if selected_grades:
        for grade in selected_grades:
            if grade in ['G11', 'G12']:
                # For G11 and G12, match all subject-specific Male/Female columns
                selected_cols_male += [col for col in data.columns if col.startswith(grade) and 'Male' in col]
                selected_cols_female += [col for col in data.columns if col.startswith(grade) and 'Female' in col]
            else:
                # For lower grades, columns are named like "G1 Male", "G1 Female", etc.
                selected_cols_male += [f"{grade} Male"]
                selected_cols_female += [f"{grade} Female"]
    else:
        # If no grades are selected, default to all available grade columns
        selected_cols_male = [col for col in grade_columns if 'Male' in col]
        selected_cols_female = [col for col in grade_columns if 'Female' in col]
    
    # Compute total enrollment based on selected gender
    if selected_gender == 'Male':
        df['Selected Grades Total'] = df[selected_cols_male].sum(axis=1)
    elif selected_gender == 'Female':
        df['Selected Grades Total'] = df[selected_cols_female].sum(axis=1)
    else:
        # If gender is "All", sum both male and female selected columns
        df['Selected Grades Total'] = df[selected_cols_male + selected_cols_female].sum(axis=1)

    # Filter out schools that have no enrollment in the selected grades and gender
    df = df[df['Selected Grades Total'] > 0]

    # Count schools by COC category and sector
    df_counts = (
        df
        .groupby(['Modified COC', 'Sector'])
        .size()
        .reset_index(name='Count')
    )
    # Ensure categories order
    coc_order = ['Purely ES', 'Purely JHS', 'Purely SHS', 'ES and JHS', 'JHS with SHS', 'All Offering']
    df_counts['Modified COC'] = pd.Categorical(df_counts['Modified COC'], categories=coc_order, ordered=True)
    df_counts = df_counts.sort_values('Modified COC')

    # Create stacked bar
    fig = px.bar(
        df_counts,
        x='Modified COC',
        y='Count',
        color='Sector',
        category_orders={
            'Modified COC': coc_order, 
            'Sector': ['Public', 'Private', 'SUCsLUCs'] # Order Sectors
            },
        labels={
            'Count': 'Number of Schools', 
            'Modified COC': 'COC Offering', 
            'Sector': 'Sector'},
        barmode='stack'
    )

    # Update the chart layout 
    fig.update_layout(
        title='School Offerings by COC Type and Sector',
        xaxis_title=None,
        yaxis_title='Number of Schools',
        legend_title='Sector',
        margin=dict(l=40, r=20, t=50, b=40),
        height=400
    )

    return fig

@app.callback(
    Output("submit-entry", "children"),
    Input("submit-entry", "n_clicks"),
    State("input-year", "value"),
    State("input-region", "value"),
    State("input-division", "value"),
    State("input-barangay", "value"),
    State("input-school", "value"),
    State("input-grade", "value"),
    State("input-gender", "value"),
    State("input-enrollment", "value"),
    prevent_initial_call=True
)
def submit_new_entry(n_clicks, year, region, division, barangay, school_id, grade, gender, enrollment):
    if not all([year, region, division, barangay, school_id, grade, gender, enrollment]):
        return "Please fill all fields."

    filename = f"data_{year}.csv"

    # If file doesn't exist, create a new one
    if not os.path.exists(filename):
        columns = ['School Year', 'BEIS School ID', 'Region', 'Division', 'Barangay', 'Total Enrollment'] + \
                  [f"{g} {s}" for g in ['K'] + [f"G{i}" for i in range(1, 13)] for s in ['Male', 'Female']]
        new_df = pd.DataFrame(columns=columns)

        # Initialize other columns to N/A
        row = {col: "N/A" for col in new_df.columns}
    else:
        new_df = pd.read_csv(filename)
        row = {col: "N/A" for col in new_df.columns}

    # Retrieve static info from schools.csv
    school_info = pd.read_csv("schools.csv")
    school_row = school_info[school_info['BEIS School ID'] == school_id].iloc[0]

    # Assign known fields
    row['School Year'] = year
    row['BEIS School ID'] = school_id
    row['Region'] = region
    row['Division'] = division
    row['Barangay'] = barangay
    row['School Name'] = school_row['School Name']
    row['Sector'] = school_row['Sector']

    # Set enrollment in correct column
    target_col = f"{grade} {gender}"
    row[target_col] = int(enrollment)
    row['Total Enrollment'] = int(enrollment)

    # Append new row to CSV
    new_df = pd.concat([new_df, pd.DataFrame([row])], ignore_index=True)
    new_df.to_csv(filename, index=False)

    return "✔ Entry Added!"

if __name__ == "__main__":
    app.run(debug=True)