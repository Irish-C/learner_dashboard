from flask import Flask, redirect, url_for, request, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Example user database
users = {
    "admin": {"password": "password123"}
}

# Initialize login functionality
def init_login(app):
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return User(user_id)
        return None

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username in users and users[username]['password'] == password:
                user = User(username)
                login_user(user)
                return redirect('/dash')  # Redirect to Dash app after login
            return "Invalid username or password", 401
        return render_template('login.html')  # Renders login.html from templates folder

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')

print("Login Page loaded")