from flask import Blueprint, render_template

home = Blueprint('dashboard', __name__, template_folder='templates')


@home.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('home/index.html')


@home.route('/')
def index():
    return render_template('home/index.html')