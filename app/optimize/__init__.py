from flask import Blueprint

bp = Blueprint('optimize', __name__)

from app.optimize import routes