from flask import Blueprint

bp = Blueprint('augmd', __name__)

from app.augmd import routes