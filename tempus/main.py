import fastapi as _fastapi
from . import apps

app = _fastapi.FastAPI()

for appname, the_app in apps.get_all_apps():
    app.mount(f"/{appname}", the_app.fastapi)
