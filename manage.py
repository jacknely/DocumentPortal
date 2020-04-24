import sys
from pathlib import Path

from app import create_app
from flask_script import Manager, Server

app = create_app("config.DevConfig")

sys.path.append(str(Path(".").absolute().parent))

manager = Manager(app)

manager.add_command(
    "runserver",
    Server(use_debugger=True, use_reloader=True, host="0.0.0.0", port=5000),
)

if __name__ == "__main__":
    manager.run()
