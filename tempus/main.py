import importlib
import fastapi

app = fastapi.FastAPI()

for modname in ["timemgmt"]:
    mod = importlib.import_module(f"tempus.{modname}")
    app.mount(f"/{modname}", mod.app)
