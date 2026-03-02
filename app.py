
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dcc, Input, Output, State, dash_table

from src.layout import children_ui, main_layout, login_page, dashboard_page, saves_page
from werkzeug.security import generate_password_hash, check_password_hash
import os
import io
from dotenv import load_dotenv
import base64
import pandas as pd
import plotly.express as px
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


server = Flask(__name__)

server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dsp_project.db'


db = SQLAlchemy(server)


app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# USER CLASS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


def add_user(email, password):
    
    if not User.query.filter_by(email=email).first():
        # PASSWORD HASHING
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return "User created successfully."
        
    else:
        return "User already exists."



def convert_to_df(csv):
   
    content_type, content_string = csv.split(',')

    
    decoded = base64.b64decode(content_string)
    
    # CSV TO PANDAS DF
    
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



    


app.layout = main_layout()




@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('login-state', 'data')
)
def display_page(pathname, login_state):
    
    if login_state == 'logged_in':
        if pathname == '/saves':
            return saves_page()
        return dashboard_page()
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
            return '/dashboard', 'logged_in', ""
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
    return '/dashboard', 'logged_in'
        

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



@app.callback(
    [Output('output-data-upload', 'children'),
     Output('stored-data', 'data'),
     Output('saved-files-table', 'data')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')],
    prevent_initial_call=True
)
def update_output(contents, filename):
    if contents is None:
        
        return [], None, []
        
    # CSV TO DF
    df = convert_to_df(contents)
    
    # DROPDOWN GRAPHING OPTIONS
    options = [{'label': i, 'value': i} for i in df.columns]
    
    file_metadata = get_file_metadata(contents, filename)

    return children_ui(filename, options, df), df.to_dict('records'), file_metadata

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('chart-type', 'value'),
    Input('stored-data', 'data'),
    prevent_initial_call=True
)
def update_graph(xaxis, yaxis, chart_type, data):
    df = pd.DataFrame(data)
    # USING SLECTED AXIS COLUMNS
    if chart_type == 'bar':
        fig = px.bar(df, x=xaxis, y=yaxis)
    elif chart_type == 'line':
        fig = px.line(df, x=xaxis, y=yaxis)
    else:
        fig = px.scatter(df, x=xaxis, y=yaxis)
        
    fig.update_layout(template="plotly_white")
    return fig


client = genai.Client(api_key=api_key)

@app.callback(
    Output('ai-response', 'children'),
    Input('ai-button', 'n_clicks'),
    State('ai-input', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call=True
)
def ask_gemini(n_clicks, user_question, data):
    
    if n_clicks > 0 and data:
        try:
            df = pd.DataFrame(data)
            
            # SMALL DATA FOR PROMPT
            columns_info = ", ".join(df.columns)
            sample_data = df.describe().to_string()
            
            prompt = f"""
            The dataset has these columns: {columns_info}
            Here is the dataset: {df}
            Here is the first 20 rows of the dataset: {df.head(20).to_string()}
            User Question: {user_question}
            
            Provide a short, analytical answer.
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
        db.create_all()  # DATABASE FILE
    
    app.run(debug=True)