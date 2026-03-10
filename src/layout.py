# src/layout.py
from dash import html, dcc, dash_table

def main_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        # Global stores that stay alive across all pages
        dcc.Store(id='login-state', storage_type='session'),
        dcc.Store(id='active-session', storage_type='session'),
        dcc.Store(id='stored-data', storage_type='memory'),
        dcc.Store(id='visuals-store', storage_type='memory'),
        html.Div(id='page-content')
    ])

def login_page():
    return html.Div([
        html.Div([
            html.H1("InsightDash", className="app-title"),
            html.P("AI Data Assistant", className="app-subtitle"),
            
            # LOGIN SECTION
            html.Div([
                html.H3("Login"),
                dcc.Input(id='login-email', type='email', placeholder='Email', className="input-field"),
                dcc.Input(id='login-password', type='password', placeholder='Password', className="input-field"),
                html.Button('Login', id='login-button', n_clicks=0, className="btn-primary"),
                html.Div(id='login-output', className="error-text")
            ], className="form-section"),

            # REGISTRATION SECTION
            html.Div([
                html.H3("Create Account"),
                dcc.Input(id='reg-email', type='email', placeholder='New Email', className="input-field"),
                dcc.Input(id='reg-password', type='password', placeholder='New Password', className="input-field"),
                html.Button('Register', id='register-button', n_clicks=0, className="btn-secondary"),
                html.Div(id='register-output', className="error-text")
            ])
        ], className="login-card")
    ], className="login-container", style={'padding': '0 15px'})

def navbar(active_page):
    """A helper function to keep the nav consistent across pages"""
    links = [
        ("Home", "/home"),
        ("Dashboard", "/dashboard"),
        ("Saves", "/saves"),
    ]
    return html.Div([
        html.Div("InsightDash", className="nav-logo"),
        html.Div([
            dcc.Link(name, href=path, className="nav-link" + (" active" if active_page == path else ""))
            for name, path in links
        ], className="nav-links-container")
    ], className="navbar")

def home_page():
    return html.Div([
        navbar('/home'),
        html.Div([
            html.H1(id='welcome-header', className="page-header"),
            html.P("Select an existing session or create a new one to get started.", className="app-subtitle", style={'textAlign': 'left'}),
            
            # CREATE NEW SESSION WIDGET
            html.Div([
                dcc.Input(id='new-session-input', type='text', placeholder='Enter new project name...', className="input-field", style={'maxWidth': '300px', 'display': 'inline-block', 'marginRight': '10px'}),
                html.Button('Create New Session', id='create-session-btn', className="btn-secondary", style={'width': 'auto', 'display': 'inline-block'})
            ], style={'marginBottom': '30px', 'padding': '20px', 'backgroundColor': '#f8fafc', 'borderRadius': '8px', 'border': '1px solid #e2e8f0'}),
            
            # THE SAVES GRID
            html.H3("Your Recent Sessions"),
            html.Div(id='sessions-grid', className='session-grid')
            
        ], className="content-card")
    ], style={'padding': '0 15px'})

def dashboard_page():
    return html.Div([
        navbar('/dashboard'),
        html.Div([
            html.H1("Dashboard", className="page-header"),
            html.Button('Logout', id='logout-button', n_clicks=0, className="btn-logout")
        ], className="header-flex"),

        # Upload card
        html.Div([
            html.H3("Data Upload"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                className="upload-box"
            ),
            html.Div(id='output-data-upload'),
        ], className="content-card"),

        html.Div([
            html.H3("Saved Files"),
            dash_table.DataTable(
                id='saved-files-table',
                columns=[
                    {'name': 'File name', 'id': 'file_name'},
                    {'name': 'Size', 'id': 'size'},
                    {'name': 'Type', 'id': 'file_type'}
                ]
            )
        ], className="content-card"),

        # Visualisation grid card
        html.Div([
            html.Div([
                html.H3("Visualisations", style={'margin': '0'}),
                html.Button('+ Add Chart', id='add-chart-btn', n_clicks=0,
                            className="btn-primary", style={'width': 'auto'})
            ], className="header-flex", style={'padding': '0', 'marginBottom': '15px'}),

            # Add-chart panel (hidden by default)
            html.Div([
                html.Div([
                    html.Label("Chart Type", style={'fontWeight': '600', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='new-chart-type',
                        options=[
                            {'label': 'Bar',       'value': 'bar'},
                            {'label': 'Line',      'value': 'line'},
                            {'label': 'Scatter',   'value': 'scatter'},
                            {'label': 'Histogram', 'value': 'histogram'},
                            {'label': 'Box Plot',  'value': 'box'},
                        ],
                        value='bar', clearable=False, style={'minWidth': '160px'}
                    ),
                ]),
                html.Div([
                    html.Label("X Axis", style={'fontWeight': '600', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(id='new-chart-x', options=[], style={'minWidth': '160px'}),
                ]),
                html.Div([
                    html.Label("Y Axis", style={'fontWeight': '600', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Dropdown(id='new-chart-y', options=[], placeholder='(auto for histogram)', style={'minWidth': '160px'}),
                ]),
                html.Div([
                    html.Label("Title", style={'fontWeight': '600', 'marginBottom': '5px', 'display': 'block'}),
                    dcc.Input(id='new-chart-title', type='text', placeholder='Chart title...',
                              style={'width': '100%', 'padding': '8px 12px', 'border': '1px solid #cbd5e1',
                                     'borderRadius': '8px', 'fontSize': '14px', 'boxSizing': 'border-box'}),
                ], style={'minWidth': '180px'}),
                html.Button('Add', id='confirm-add-chart-btn', n_clicks=0,
                            className="btn-primary", style={'width': 'auto', 'alignSelf': 'flex-end'}),
            ], id='add-chart-panel', style={
                'display': 'none', 'flexWrap': 'wrap', 'gap': '15px',
                'padding': '15px', 'backgroundColor': '#f8fafc', 'borderRadius': '8px',
                'marginBottom': '20px', 'alignItems': 'flex-end', 'border': '1px solid #e2e8f0'
            }),

            html.Div(id='viz-grid'),
        ], className="content-card"),

        html.Div([
            html.H3("Assistant Data Settings"),
            html.P("Choose how many rows from the CSV to include in the AI prompt.",
                   style={'marginTop': '0', 'color': '#64748b'}),
            html.Div([
                html.Label("Sample Size (rows)", style={'fontWeight': '600'}),
                dcc.Input(
                    id='ai-sample-size',
                    type='number',
                    value=50,
                    min=1,
                    step=1,
                    className='input-field',
                    style={'maxWidth': '240px', 'marginBottom': '0'}
                )
            ])
        ], className="content-card"),

        html.Div([
            html.H3("Ask your Data Assistant"),
            dcc.Textarea(id='ai-input', placeholder='e.g., "What are the main trends?"', className="ai-textarea"),
            html.Button('Ask AI', id='ai-button', n_clicks=0, className="btn-ai"),
            html.Div(id='ai-response', className="ai-response-box")
        ], className="content-card")
    ], style={'padding': '0 15px'})

def saves_page():
    return html.Div([
        navbar('/saves'),
        html.Div([
            html.H1("Saves", className="page-header"),
            html.Button('Logout', id='logout-button', n_clicks=0, className="btn-logout")
        ], className="header-flex"),
        
        html.Div([
            html.H3("Data Upload"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                className="upload-box"
            ),
        ], className="content-card"),

        html.Div([
            html.H3("Saved Files"),
            dash_table.DataTable(
                id='saved-files-table',
                columns=[
                    {'name': 'File name', 'id': 'file_name'},
                    {'name': 'Size', 'id': 'size'},
                    {'name': 'Type', 'id': 'file_type'}
                ]
            )
        ], className="content-card"),
        
        html.Div(id='output-data-upload')
    ], style={'padding': '0 15px'})

def data_loaded_banner(filename, n_rows, n_cols):
    """Simple banner shown after a dataset is loaded."""
    return html.Div([
        html.Span("✓  ", style={'color': '#10b981', 'fontWeight': '700'}),
        html.Span(
            f"Loaded: {filename}  ·  {n_rows:,} rows  ·  {n_cols} columns",
            style={'color': '#475569', 'fontSize': '14px'}
        )
    ], style={'marginTop': '12px', 'padding': '10px 14px', 'backgroundColor': '#f0fdf4',
              'borderRadius': '6px', 'border': '1px solid #86efac'})