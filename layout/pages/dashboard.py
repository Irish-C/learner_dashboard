from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import plotly.express as px
import pandas as pd

correct_region_order = [
    'CAR', 'NCR', 'Region I', 'Region II', 'Region III', 'Region IV-A',
    'MIMAROPA', 'Region V', 'Region VI', 'Region VII', 'Region VIII',
    'Region IX', 'Region X', 'Region XI', 'Region XII', 'CARAGA', 'BARMM'
]

def prepare_strand_gender_chart(data, grade):
    strands = ['ABM', 'HUMSS', 'STEM', 'GAS', 'PBM', 'TVL', 'SPORTS', 'ARTS']
    reshaped_data = []

    for strand in strands:
        if strand in ['TVL', 'SPORTS', 'ARTS']:
            male_col = f'{grade} {strand} Male'
            female_col = f'{grade} {strand} Female'
        else:
            male_col = f'{grade} ACAD - {strand} Male'
            female_col = f'{grade} ACAD - {strand} Female'

        if male_col in data.columns and female_col in data.columns:
            reshaped_data.extend([
                {'Strand': strand, 'Gender': 'Male', 'Enrollment': data[male_col].sum()},
                {'Strand': strand, 'Gender': 'Female', 'Enrollment': data[female_col].sum()}
            ])

    df_strand_gender = pd.DataFrame(reshaped_data)

    fig = px.bar(
        df_strand_gender,
        x='Strand',
        y='Enrollment',
        color='Gender',
        barmode='group',
        title=f'Enrollment by SHS Strand and Gender ({grade})',
        labels={'Enrollment': 'Total Enrollment'}
    )
    return fig


def dashboard_content(data, grade_options, region_options, school_dropdown_options, combined_shs_track_df):
    return dbc.Container(

        fluid=True,
        children=[
            html.H1("Dashboard", className="page-title"),
            html.P(f"Welcome Back, Teacher!", className="subtitle"),
            html.Br(),
            # ✅ Always-present KPI row BEFORE the chart columns
            html.Div(id='kpi_card_row', className='mb-4'),

            dbc.Row([
                # 🎛️ Filter Panel
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Filter Control Panel")),
                        dbc.CardBody([
                            html.Br(),
                            html.Label("School Year:"),
                            dcc.Dropdown(
                                id='school_year_filter',
                                options=[{'label': sy, 'value': sy} for sy in sorted(data['School Year'].unique(), reverse=True)],
                                value=sorted(data['School Year'].unique(), reverse=True)[0],
                                placeholder='Select School Year'
                            ),
                            html.Label("Region:"),
                            dcc.Dropdown(
                                id='region_filter',
                                options=region_options,
                                multi=True,
                                placeholder='Select Region'
                            ),
                            html.Br(),
                            html.Label("Grade Level:"),
                            dcc.Dropdown(
                                id='grade_filter',
                                options=grade_options,
                                multi=True,
                                placeholder='Select Grade Level'
                            ),
                            html.Br(),
                            html.Label("Gender:"),
                            dcc.RadioItems(
                                id='gender_filter',
                                options=[
                                    {'label': 'Male', 'value': 'Male'},
                                    {'label': 'Female', 'value': 'Female'},
                                    {'label': 'All', 'value': 'All'}
                                ],
                                value='All',
                                inline=True,
                                labelStyle={'margin-right': '15px'}
                            ),
                            html.Br(),
                            html.Label("Search School:"),
                            dcc.Dropdown(
                                id='school_search',
                                options=school_dropdown_options,
                                placeholder='Search by School ID or Name',
                                searchable=True
                            ),
                            html.Br(),
                            dbc.Modal(
                                id='school_modal',
                                is_open=False,
                                children=[
                                    dbc.ModalHeader(dbc.ModalTitle(id='modal_school_name')),
                                    dbc.ModalBody(id='modal_school_body'),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="modal_close_btn", className="ms-auto", n_clicks=0)
                                    )
                                ]
                            )
                        ])
                    ]),
                    width=3
                ),
                # 📊 Tabs with Charts
                dbc.Col([
                    dcc.Tabs([
                    dcc.Tab(label='📊 Overview', children=[
                        # Region-wise Enrollment
                        dbc.Card([dbc.CardBody([dcc.Graph(
                            id='enrollment_bar_chart',
                            figure=px.bar(
                                data.groupby('Region').agg({'Total Male': 'sum', 'Total Female': 'sum'}).assign(
                                    Total=lambda df: df['Total Male'] + df['Total Female']
                                ).reindex(correct_region_order).reset_index(),
                                x='Region',
                                y='Total',
                                title='Total Enrollment by Region',
                                text='Total',
                                color='Region'
                            ).update_layout(xaxis_title='Region', yaxis_title='Total Enrollment')
                        )])], className="mb-4"),
                        # Gender Distribution Pie Chart
                        dbc.Card([dbc.CardBody([dcc.Graph(
                            id='gender_pie_chart',
                            figure=px.pie(
                                names=['Male', 'Female'],
                                values=[
                                    data[[col for col in data.columns if 'Male' in col]].sum().sum(),
                                    data[[col for col in data.columns if 'Female' in col]].sum().sum()
                                ],
                                title='Total Learners by Gender',
                                hole=0.6,
                                color_discrete_sequence=['#3498db', '#e74c3c']
                            ).update_traces(textinfo='percent+label')
                        )])], className="mb-4"),                        
                        # G11 Strand by Gender
                        dbc.Card([dbc.CardBody([dcc.Graph(
                            figure=prepare_strand_gender_chart(data, 'G11')
                        )])], className="mb-4"),
                        # G12 Strand by Gender
                        dbc.Card([dbc.CardBody([dcc.Graph(
                            figure=prepare_strand_gender_chart(data, 'G12')
                        )])], className="mb-4"),
                    ]),

                        dcc.Tab(label='🧑‍🏫 SHS Track Analysis', children=[
                        # SHS Track Total Enrollment Horizontal Bar Chart
                        dbc.Card([dbc.CardBody([dcc.Graph(
                            id='shs_track_bar_chart',
                            figure=px.bar(
                                combined_shs_track_df,
                                x='Total Enrollment',
                                y='Track',
                                color='Grade Level',
                                orientation='h',
                                title='SHS Track Total Enrollment',
                                text='Total Enrollment'
                            ).update_layout(xaxis_title='Total Enrollment', yaxis_title='Track')
                        )])], className="mb-4"),

                        ]),
                        dcc.Tab(label='🗺️ Regional & Division Insights', children=[
                            dbc.Card([dbc.CardBody([dcc.Graph(id='enrollment_vs_schools_chart')])], className="mb-4")
                        ]),
                        dcc.Tab(label='📋 Table View', children=[
                            html.H4("Enrollment Table"),
                            dash_table.DataTable(
                                id='enrollment_table',
                                columns=[
                                    {'name': 'Region', 'id': 'Region'},
                                    {'name': 'Division', 'id': 'Division'},
                                    {'name': 'Total Male', 'id': 'Total Male', 'type': 'numeric'},
                                    {'name': 'Total Female', 'id': 'Total Female', 'type': 'numeric'},
                                    {'name': 'Total Enrollment', 'id': 'Total Enrollment', 'type': 'numeric'}
                                ],
                                data=data[['Region', 'Division', 'Total Male', 'Total Female', 'Total Enrollment']].to_dict('records'),
                                page_size=10,
                                sort_action='native',
                                filter_action='native',
                                style_table={'overflowX': 'auto'}
                            )
                        ])
                    ])
                ], width=9)
            ]),

            html.Hr()
        ]
    )
