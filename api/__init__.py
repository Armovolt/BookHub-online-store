from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Імпортуємо маршрути після створення Blueprint, щоб уникнути циркулярних імпортів
from . import routes