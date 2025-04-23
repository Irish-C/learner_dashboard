from flask import Flask, redirect, url_for, request, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for sessions

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'  # Define the login view route

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Example user database (for demonstration purposes)
users = {
    "admin": {"password": "password123"},
    # You can add more users here
}

# Initialize login functionality
def init_login(app):
    login_manager.init_app(app)

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return User(user_id)
        return None

    # Login route for the application
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
        return render_template('login.html')  # Render login template

    # Logout route (requires user to be logged in)
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')  # Redirect back to login after logging out

    # Dashboard route (requires user to be logged in)
    @app.route('/dash')
    @login_required
    def dashboard():
        return render_template('dashboard.html')  # Replace with your Dash content page


# Initialize the login manager
init_login(app)

if __name__ == '__main__':
    app.run(debug=True)