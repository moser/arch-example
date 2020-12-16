import fastapi as _fastapi
import a2wsgi as _a2wsgi

from legacy import wsgi as _legacy_wsgi
from . import apps

from .lib import legacy_app

# TODO the legacy app thing should be a proper wrapper around the django app
# that acts like the "TheApp" objects.
legacy_app.init()
app = _fastapi.FastAPI()

for appname, the_app in apps.get_all_apps():
    app.mount(f"/{appname}", the_app.fastapi)

app.mount(f"/legacy", _a2wsgi.WSGIMiddleware(_legacy_wsgi.application))
