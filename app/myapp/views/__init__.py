# This __init__.py file marks the 'views' directory as a Python package.
# You need to explicitly import view classes here, like so:
#     from .render_views import MyRenderView
#     from .auth_views import LoginView

# Only include imports for views that should be available at the package level to avoid unnecessary namespace pollution.

from .chat_bubble import chat_bubble_view
from .delete_views import *
from .form_views import *
from .json_views import *
from .page_views import *
