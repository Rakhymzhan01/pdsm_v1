import dash_bootstrap_components as dbc
from dash import Dash, html, page_container, callback, Output, Input, State

from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime


server = Flask(__name__)
app = Dash(__name__, use_pages=True, 
           external_stylesheets=[
               dbc.themes.UNITED, 
               dbc.icons.BOOTSTRAP, 
               'https://fonts.googleapis.com/css?family=Audiowide'
           ],
           # external_scripts=[
           #     "https://cdn.zingchart.com/zingchart.min.js"
           # ],
           server=server, suppress_callback_exceptions=True
        )

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        {%favicon%}
        {%css%}
        <script src="https://cdn.zingchart.com/zingchart.min.js"></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:akzhol2030@86.107.198.48:5432/karatobe"
server.config['SECRET_KEY'] = 'sfgwerthggrnbsdfvstghernsdfvaergfv34g2rbvsdfv'
db = SQLAlchemy(server)
bcrypt = Bcrypt(app)

"""Login manager object will be used to login / logout users"""
login_manager = LoginManager(server)
login_manager.init_app(server)
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_level = db.Column(db.String(60), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.layout = html.Div(children=[
	page_container
])


'''Callbacks--------------------------------------------'''
@callback(
    Output("output-state", "children"),
    Input("login-button", "n_clicks"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    prevent_initial_call=True,
)
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            """Save this user to Log File"""
            if True:
                with open('./assets/user_login.csv', 'a') as f:
                    f.write(f'{current_user.username} logged in {datetime.now()}\n')
                f.close()
            return [
                html.Meta(httpEquiv="refresh", content="0.5")
            ]
        else:
            return "Неверное имя пользователя или неверный пароль!"


@callback(
    Output('password_changed_placeholder', 'children'),
    Input('change_button', 'n_clicks'),
    State('password', 'value'),
    State('re-enter-password', 'value')
)
def change_password(n_clicks, password, re_entered_password):
    if n_clicks > 0:
        if password == re_entered_password:
            bcrypt_password = bcrypt.generate_password_hash(password).decode('utf-8')
            current_user.password = bcrypt_password
            db.session.commit()
            return [
                html.Plaintext("Изменения сохранены.",
                               style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
            ]
        elif password != re_entered_password:
            return [
                html.Plaintext("Повторно введенный пароль не совпадает.",
                               style={'color': 'red', 'font-weight': 'bold', 'font-size': 'large'})
            ]



if __name__ == "__main__":
    server.run(debug=True)
