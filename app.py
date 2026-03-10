# app.py
# app.py
from flask import Flask
from dash import Dash, html, dcc, Input, Output, State, dash_table, no_update, ctx, MATCH, ALL
import os
import io
import base64
import uuid
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from google import genai
from werkzeug.security import check_password_hash

# Import from your modular files
from src.layout import data_loaded_banner, main_layout, login_page, dashboard_page, saves_page, home_page
from src.models import db, User, add_user, ProjectSession, create_session, save_session_data, load_session_data, save_visuals

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Initialize Flask Server
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dsp_project.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
server.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-default-key") 

# 3. Bind the Database to the Flask App
db.init_app(server)

# 4. Initialize Dash App
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# --- HELPER FUNCTIONS ---
def convert_to_df(csv):
    content_type, content_string = csv.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df

def get_file_metadata(contents, filename):
    if not contents or not filename:
        return []

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    size_bytes = len(decoded)

    if size_bytes < 1024:
        size_display = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_display = f"{size_bytes / 1024:.1f} KB"
    else:
        size_display = f"{size_bytes / (1024 * 1024):.1f} MB"

    file_type = filename.split('.')[-1].upper() if '.' in filename else 'UNKNOWN'

    return [{
        'file_name': filename,
        'size': size_display,
        'file_type': file_type
    }]

# --- LAYOUT ---
app.layout = main_layout()


# --- FIGURE BUILDER ---
def make_figure(viz, df):
    chart_type = viz.get('type', 'bar')
    x = viz.get('x')
    y = viz.get('y')
    title = viz.get('title', '')
    try:
        if chart_type == 'histogram':
            fig = px.histogram(df, x=x, title=title)
        elif chart_type == 'box':
            fig = px.box(df, x=x, y=y, title=title) if y else px.box(df, y=x, title=title)
        elif chart_type == 'bar':
            fig = px.bar(df, x=x, y=y, title=title)
        elif chart_type == 'line':
            fig = px.line(df, x=x, y=y, title=title)
        else:  # scatter
            fig = px.scatter(df, x=x, y=y, title=title)
        fig.update_layout(
            template='plotly_white',
            margin=dict(l=30, r=30, t=40, b=30),
            font=dict(size=11),
            title_font_size=13,
            height=340
        )
    except Exception:
        fig = px.scatter(title='Error – check column selection')
        fig.update_layout(template='plotly_white', height=340)
    return fig

# --- ROUTING & AUTH CALLBACKS ---
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('login-state', 'data')
)
def display_page(pathname, login_state):
    # Check if user is logged in by looking for a dictionary with user_id
    if login_state and isinstance(login_state, dict) and 'user_id' in login_state:
        if pathname == '/dashboard':
            return dashboard_page()
        elif pathname == '/saves':
            return saves_page()
        else:
            return home_page() # Default to Home
    else:
        return login_page()

@app.callback(
    [Output('url', 'pathname'),
     Output('login-state', 'data'),
     Output('login-output', 'children')],
    Input('login-button', 'n_clicks'),
    State('login-email', 'value'),
    State('login-password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    if n_clicks > 0:
        if not email or not password:
            return '/login', None, "Please provide both email and password."
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # STORE USER DATA IN SESSION
            user_data = {'user_id': user.id, 'email': user.email}
            return '/home', user_data, ""
        else:
            return '/login', None, "Invalid email or password."
    return '/login', None, ""

@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('login-state', 'data', allow_duplicate=True)],
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks > 0:
        return '/login', None
    return no_update, no_update

@app.callback(
    Output('register-output', 'children'),
    Input('register-button', 'n_clicks'),
    State('reg-email', 'value'),
    State('reg-password', 'value'),
    prevent_initial_call=True
)
def handle_registration(n_clicks, email, password):
    if n_clicks > 0:
        if not email or not password:
            return "Please provide both email and password."
        else:
            return add_user(email, password)

# --- HOME PAGE LOAD CALLBACK ---
@app.callback(
    [Output('welcome-header', 'children'),
     Output('sessions-grid', 'children')],
    Input('url', 'pathname'),
    State('login-state', 'data')
)
def load_home_page(pathname, login_state):
    # Make sure we have a user
    if not login_state or 'user_id' not in login_state:
        return "", []
        
    # Only update if on home page
    if pathname != '/home':
        return no_update, no_update
        
    user_id = login_state['user_id']
    welcome_msg = f"Welcome back, {login_state['email'].split('@')[0]}!"

    # Load the sessions grid
    sessions = ProjectSession.query.filter_by(user_id=user_id).order_by(ProjectSession.created_at.desc()).all()
    
    if not sessions:
        grid_ui = html.Div("No saved sessions yet. Create one above!", style={'color': '#64748b'})
    else:
        grid_ui = []
        for s in sessions:
            card = html.Div([
                html.H4(s.name, style={'margin': '0 0 10px 0', 'color': '#1e3a8a'}),
                html.P(f"Created: {s.created_at.strftime('%Y-%m-%d')}", style={'fontSize': '12px', 'color': '#64748b', 'margin': '0'}),
                html.Button("Open", id={'type': 'open-session-btn', 'index': s.id}, className="btn-primary", style={'marginTop': '15px'})
            ], className="session-card")
            grid_ui.append(card)

    return welcome_msg, grid_ui

# --- CREATE SESSION CALLBACK ---
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('active-session', 'data', allow_duplicate=True),
     Output('new-session-input', 'value', allow_duplicate=True)],
    Input('create-session-btn', 'n_clicks'),
    [State('login-state', 'data'),
     State('new-session-input', 'value')],
    prevent_initial_call=True
)
def create_new_session(n_clicks, login_state, new_session_name):
    # Make sure we have a user
    if not login_state or 'user_id' not in login_state:
        return no_update, no_update, no_update
        
    if n_clicks and n_clicks > 0 and new_session_name:
        user_id = login_state['user_id']
        session_id = create_session(new_session_name, user_id)
        active_data = {'session_id': session_id, 'name': new_session_name}
        return '/dashboard', active_data, ''

    return no_update, no_update, no_update

# --- GRID BUTTON CALLBACK (THE NEW ADDITION) ---
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('active-session', 'data', allow_duplicate=True)],
    Input({'type': 'open-session-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def open_session_from_grid(n_clicks_list):
    # Check if any button was actually clicked
    if not any(n_clicks_list):
        return no_update, no_update
        
    # Get the ID of the specific button that was clicked
    clicked_button_id = ctx.triggered_id
    if clicked_button_id:
        session_id = clicked_button_id['index']
        # Fetch the session name from DB
        session = db.session.get(ProjectSession, session_id)
        if session:
            active_data = {'session_id': session.id, 'name': session.name}
            return '/dashboard', active_data
            
    return no_update, no_update

# --- DASHBOARD & DATA CALLBACKS ---
@app.callback(
    [Output('output-data-upload', 'children', allow_duplicate=True),
     Output('stored-data', 'data', allow_duplicate=True),
     Output('saved-files-table', 'data', allow_duplicate=True)],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('active-session', 'data')],
    prevent_initial_call=True
)
def update_output(contents, filename, active_session):
    if contents is None:
        return no_update, no_update, no_update

    df = convert_to_df(contents)
    file_metadata = get_file_metadata(contents, filename)

    if active_session and 'session_id' in active_session:
        save_session_data(
            session_id=active_session['session_id'],
            filename=filename,
            records=df.to_dict('records'),
            file_metadata=file_metadata
        )

    banner = data_loaded_banner(filename, len(df), len(df.columns))
    return banner, df.to_dict('records'), file_metadata


@app.callback(
    [Output('output-data-upload', 'children', allow_duplicate=True),
     Output('stored-data', 'data', allow_duplicate=True),
     Output('saved-files-table', 'data', allow_duplicate=True),
     Output('visuals-store', 'data', allow_duplicate=True)],
    Input('output-data-upload', 'id'),
    State('active-session', 'data'),
    prevent_initial_call=True
)
def restore_dashboard_state(_, active_session):
    if not active_session or 'session_id' not in active_session:
        return [], None, [], []

    session_state = load_session_data(active_session['session_id'])
    if not session_state or not session_state['records']:
        empty_visuals = session_state.get('visuals', []) if session_state else []
        return [], None, [], empty_visuals

    df = pd.DataFrame(session_state['records'])
    filename = session_state.get('filename') or 'saved_dataset.csv'
    banner = data_loaded_banner(filename, len(df), len(df.columns))

    return banner, session_state['records'], session_state.get('file_metadata', []), session_state.get('visuals', [])

# --- VIZ GRID CALLBACKS ---

@app.callback(
    Output('add-chart-panel', 'style'),
    Input('add-chart-btn', 'n_clicks'),
    State('add-chart-panel', 'style'),
    prevent_initial_call=True
)
def toggle_add_panel(n_clicks, current_style):
    if not n_clicks:
        return no_update
    base = dict(current_style)
    base['display'] = 'flex' if n_clicks % 2 == 1 else 'none'
    return base


@app.callback(
    [Output('new-chart-x', 'options'),
     Output('new-chart-y', 'options')],
    Input('stored-data', 'data'),
    prevent_initial_call=True
)
def populate_column_options(data):
    if not data:
        return [], []
    df = pd.DataFrame(data)
    options = [{'label': col, 'value': col} for col in df.columns]
    return options, options


@app.callback(
    Output('viz-grid', 'children'),
    [Input('visuals-store', 'data'),
     Input('stored-data', 'data')]
)
def render_viz_grid(visuals, stored_data):
    if not stored_data:
        return html.P("Upload a dataset above to start building charts.",
                      style={'color': '#64748b', 'padding': '20px 0'})
    if not visuals:
        return html.P("Click '+ Add Chart' to create your first visualisation.",
                      style={'color': '#64748b', 'padding': '20px 0'})
    df = pd.DataFrame(stored_data)
    cards = []
    for viz in visuals:
        card = html.Div([
            html.Div([
                html.Strong(viz.get('title', 'Chart'),
                            style={'color': '#1e3a8a', 'fontSize': '14px'}),
                html.Button('✕', id={'type': 'viz-delete', 'index': viz['id']},
                            n_clicks=0,
                            style={'background': 'none', 'border': 'none', 'cursor': 'pointer',
                                   'fontSize': '18px', 'color': '#94a3b8', 'padding': '0',
                                   'lineHeight': '1'})
            ], style={'display': 'flex', 'justifyContent': 'space-between',
                      'alignItems': 'center', 'marginBottom': '8px'}),
            dcc.Graph(figure=make_figure(viz, df),
                      config={'displayModeBar': True, 'displaylogo': False},
                      style={'height': '340px'})
        ], className='viz-card')
        cards.append(card)
    return html.Div(cards, className='viz-grid')


@app.callback(
    [Output('visuals-store', 'data', allow_duplicate=True),
     Output('new-chart-title', 'value')],
    Input('confirm-add-chart-btn', 'n_clicks'),
    [State('new-chart-type', 'value'),
     State('new-chart-x', 'value'),
     State('new-chart-y', 'value'),
     State('new-chart-title', 'value'),
     State('visuals-store', 'data'),
     State('stored-data', 'data'),
     State('active-session', 'data')],
    prevent_initial_call=True
)
def add_visual(n_clicks, chart_type, x_col, y_col, title, visuals, stored_data, active_session):
    if not n_clicks or not stored_data or not x_col:
        return no_update, no_update
    visuals = list(visuals or [])
    new_id = f"viz_{uuid.uuid4().hex[:8]}"
    new_visual = {
        'id': new_id,
        'type': chart_type or 'bar',
        'x': x_col,
        'y': y_col,
        'title': title.strip() if title else f'{(chart_type or "Chart").title()} \u2013 {x_col}'
    }
    visuals.append(new_visual)
    if active_session and 'session_id' in active_session:
        save_visuals(active_session['session_id'], visuals)
    return visuals, ''


@app.callback(
    Output('visuals-store', 'data', allow_duplicate=True),
    Input({'type': 'viz-delete', 'index': ALL}, 'n_clicks'),
    [State('visuals-store', 'data'),
     State('active-session', 'data')],
    prevent_initial_call=True
)
def delete_visual(n_clicks_list, visuals, active_session):
    if not any(n_clicks_list) or not visuals:
        return no_update
    triggered = ctx.triggered_id
    if not triggered:
        return no_update
    viz_id = triggered['index']
    visuals = [v for v in visuals if v['id'] != viz_id]
    if active_session and 'session_id' in active_session:
        save_visuals(active_session['session_id'], visuals)
    return visuals


client = genai.Client(api_key=api_key)

@app.callback(
    Output('ai-response', 'children'),
    Input('ai-button', 'n_clicks'),
    State('ai-input', 'value'),
    State('stored-data', 'data'),
    State('visuals-store', 'data'),
    State('ai-sample-size', 'value'),
    prevent_initial_call=True
)
def ask_gemini(n_clicks, user_question, data, visuals, sample_size):
    if n_clicks > 0 and data:
        try:
            df = pd.DataFrame(data)
            columns_info = ", ".join(df.columns)

            # Use user-selected sample size, capped by dataset length.
            safe_sample_size = int(sample_size) if sample_size and int(sample_size) > 0 else 50
            safe_sample_size = min(safe_sample_size, len(df))
            sample_df = df.head(safe_sample_size)

            visuals = visuals or []
            if visuals:
                visual_summary_lines = []
                for idx, viz in enumerate(visuals, start=1):
                    visual_summary_lines.append(
                        f"{idx}. type={viz.get('type', 'unknown')}, title={viz.get('title', '')}, x={viz.get('x', '')}, y={viz.get('y', '')}"
                    )
                visuals_summary = "\n".join(visual_summary_lines)
            else:
                visuals_summary = "No visuals created yet."

            # Add simple descriptive statistics for numeric columns.
            numeric_stats = "No numeric columns found."
            numeric_df = sample_df.select_dtypes(include='number')
            if not numeric_df.empty:
                numeric_stats = numeric_df.describe().transpose().to_string()
            
            prompt = f"""
            You are a data assistant helping explain a user-built dashboard.

            Dataset columns:
            {columns_info}

            Dataset total rows: {len(df)}
            Rows included in this prompt sample: {safe_sample_size}

            Dashboard visuals configuration:
            {visuals_summary}

            Numeric column summary (sample):
            {numeric_stats}

            Sample rows:
            {sample_df.to_string(index=False)}

            User question:
            {user_question}
            
            Instructions:
            1) Explain trends in plain language.
            2) Reference relevant visuals by title/type where possible.
            3) Mention confidence limits because only a sample may be used.
            4) End with 2 suggested follow-up analyses.
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "FREE TIER BUSY"
            return f"AI Error: {error_msg}"
    elif not data:
        return "Please upload a dataset first."
    return ""

# RUN
if __name__ == '__main__':
    with server.app_context():
        db.create_all()
        # Migrate: add visuals_json column to existing DBs that predate this feature
        from sqlalchemy import inspect as sa_inspect, text as sa_text
        insp = sa_inspect(db.engine)
        if db.engine.dialect.has_table(db.engine.connect(), 'session_data'):
            existing_cols = [c['name'] for c in insp.get_columns('session_data')]
            if 'visuals_json' not in existing_cols:
                with db.engine.connect() as conn:
                    conn.execute(sa_text("ALTER TABLE session_data ADD COLUMN visuals_json TEXT DEFAULT '[]'"))
                    conn.commit()

    app.run(debug=True)