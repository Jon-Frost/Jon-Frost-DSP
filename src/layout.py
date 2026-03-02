from dash import html, dcc, dash_table

def main_layout():
    
    return html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='login-state', storage_type='session'),
        html.Div(id='page-content')
    ])

def login_page():
    
    input_style = {
        'width': '100%',
        'padding': '12px',
        'marginBottom': '12px',
        'border': '1px solid #cfd8e3',
        'borderRadius': '8px',
        'fontSize': '14px'
    }

    button_style = {
        'width': '100%',
        'padding': '12px',
        'backgroundColor': '#2563eb',
        'color': 'white',
        'border': 'none',
        'borderRadius': '8px',
        'fontWeight': '600',
        'cursor': 'pointer'
    }

    return html.Div([
        html.Div([
            html.H1("InsightDash", style={'textAlign': 'center', 'color': '#1f2a44', 'marginBottom': '8px'}),
            html.P("AI Data Assistant", style={'textAlign': 'center', 'color': '#5b6b8c', 'marginTop': '0'}),
            
            html.Div([
                # LOGIN
                html.Div([
                    html.H3("Login", style={'marginBottom': '12px', 'color': '#1f2a44'}),
                    dcc.Input(id='login-email', type='email', placeholder='Email', style=input_style),
                    dcc.Input(id='login-password', type='password', placeholder='Password', style=input_style),
                    html.Button('Login', id='login-button', n_clicks=0, style=button_style),
                    html.Div(id='login-output', style={'marginTop': '8px', 'color': '#b91c1c'})
                ], style={'marginBottom': '16px'}),

                # REGISTRATION
                html.Div([
                    html.H3("Create Account", style={'marginBottom': '12px', 'color': '#1f2a44'}),
                    dcc.Input(id='reg-email', type='email', placeholder='New Email', style=input_style),
                    dcc.Input(id='reg-password', type='password', placeholder='New Password', style=input_style),
                    html.Button('Register', id='register-button', n_clicks=0, style={**button_style, 'backgroundColor': '#10b981'}),
                    html.Div(id='register-output', style={'marginTop': '8px', 'color': '#b91c1c'})
                ])
            ])
        ], style={
            'width': '100%',
            'maxWidth': '420px',
            'backgroundColor': 'white',
            'padding': '28px',
            'borderRadius': '14px',
            'boxShadow': '0 10px 30px rgba(15, 23, 42, 0.12)'
        })
    ], style={
        'minHeight': '100vh',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'backgroundColor': '#eaf4ff',
        'padding': '24px'
    })

def dashboard_page():
    #SEPARATE TO LOGIN PAGE
    return html.Div([
        html.Div([
            html.Div("InsightDash", style={
                'fontWeight': '700',
                'fontSize': '20px',
                'color': '#1f2a44'
            }),
            html.Div([
                dcc.Link("Account", href='/account', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'}),
                dcc.Link("Assistant", href='/assistant', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'}),
                dcc.Link("Saves", href='/saves', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'}),
                dcc.Link("Dashboard", href='/dashboard', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none', 'fontWeight': '600'})
            ], style={'display': 'flex', 'gap': '6px', 'color': '#1f2a44'})
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'padding': '14px 20px',
            'backgroundColor': '#f8fbff',
            'borderBottom': '1px solid #e2e8f0',
            'position': 'sticky',
            'top': '0',
            'zIndex': '10'
        }),
        html.Div([
            html.H1("InsightDash Dashboard", style={'display': 'inline-block'}),
            html.Button('Logout', id='logout-button', n_clicks=0, 
                       style={'float': 'right', 'marginTop': '20px'})
        ], style={'borderBottom': '2px solid #007bff', 'paddingBottom': '10px'}),

        # QUERY SECTION
        html.Div([
            html.H3("Ask your Data Assistant"),
            dcc.Textarea(
                id='ai-input',
                placeholder='e.g., "What are the main trends in this data?"',
                style={'width': '100%', 'height': '100px'}
            ),
            html.Br(),
            html.Button('Ask AI', id='ai-button', n_clicks=0),
            html.Div(id='ai-response', style={'padding': '15px', 'backgroundColor': '#f9f9f9', 'marginTop': '10px'})
        ], style={'padding': '20px', 'border': '1px solid #007bff', 'marginTop': '20px', 'borderRadius': '8px'}),
        dcc.Store(id='stored-data')
    ])

def saves_page():
    table_columns = [
        {'name': 'File name', 'id': 'file_name'},
        {'name': 'Size', 'id': 'size'},
        {'name': 'File type', 'id': 'file_type'}
    ]

    table_data = []

    return html.Div([
        html.Div([
            html.Div("InsightDash", style={
                'fontWeight': '700',
                'fontSize': '20px',
                'color': '#1f2a44'
            }),
            html.Div([
                dcc.Link("Account", href='/account', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'}),
                dcc.Link("Assistant", href='/assistant', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'}),
                dcc.Link("Saves", href='/saves', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none', 'fontWeight': '600'}),
                dcc.Link("Dashboard", href='/dashboard', style={'padding': '8px 12px', 'color': '#1f2a44', 'textDecoration': 'none'})
                
            ], style={'display': 'flex', 'gap': '6px', 'color': '#1f2a44'})
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'space-between',
            'padding': '14px 20px',
            'backgroundColor': '#f8fbff',
            'borderBottom': '1px solid #e2e8f0',
            'position': 'sticky',
            'top': '0',
            'zIndex': '10'
        }),
        html.Div([
            html.H1("Saves", style={'display': 'inline-block'}),
            html.Button('Logout', id='logout-button', n_clicks=0, 
                       style={'float': 'right', 'marginTop': '20px'})
        ], style={'borderBottom': '2px solid #007bff', 'paddingBottom': '10px'}),
        html.Div([
            html.H3("Data Upload"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed',
                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                }
            ),
        ]),
        html.Div([
            html.H3("Saved Files"),
            dash_table.DataTable(
                id='saved-files-table',
                columns=table_columns,
                data=table_data,
                style_table={'width': '100%', 'overflowX': 'auto'},
                style_header={'backgroundColor': '#f1f5f9', 'fontWeight': '600'},
                style_cell={'padding': '10px', 'textAlign': 'left'}
            )
        ], style={'marginTop': '20px'}),
        html.Div(id='output-data-upload'),
        dcc.Store(id='stored-data')
    ]),
        

def children_ui(filename, options, df):

    return html.Div([
        html.H5(f"Analyzing: {filename}"),
        
        html.Div([
            html.Div([
                html.Label("Select X-Axis:"),
                dcc.Dropdown(id='xaxis-column', options=options, value=df.columns[0]),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Select Y-Axis:"),
                dcc.Dropdown(id='yaxis-column', options=options, value=df.columns[1] if len(df.columns) > 1 else df.columns[0]),
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
        ], style={'padding': '20px'}),

        
html.Div([
    html.Label("Select Chart Type:"),
    dcc.Dropdown(
        id='chart-type',
        options=[
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Bar Chart', 'value': 'bar'},
            {'label': 'Line Chart', 'value': 'line'}
        ],
        value='scatter'
        ),
        ], 
        style={'width': '100%', 'padding': '10px'}),

        dcc.Graph(id='indicator-graphic'),

        html.Hr(),
        dash_table.DataTable(
            data=df.head(5).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ])