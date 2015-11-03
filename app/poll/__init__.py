from flask import Blueprint

poll = Blueprint('poll', __name__)

from . import views, errors
from ..models import Permission


@poll.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
