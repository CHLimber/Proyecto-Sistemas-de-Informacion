import sys
import os

project_home = '/home/TUNOMBREDEUSUARIO/ServiControl/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app

application = create_app('production')
