from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Імпортуємо маршрути після створення Blueprint
from . import routes