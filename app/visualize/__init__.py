from flask import Blueprint

bp = Blueprint('visualize', __name__)

from app.visualize import routes