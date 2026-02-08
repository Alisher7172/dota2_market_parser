import sys
import os
from pathlib import Path

project_home = '/home/alisherbek12/clo'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
env_path = Path(project_home) / '.env'
load_dotenv(dotenv_path=env_path)

from app import app as application