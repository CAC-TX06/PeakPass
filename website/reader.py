import os
from pathlib import Path
import yaml

os.chdir(Path(__file__).parent.parent)
ABS_PATH = Path(os.getcwd())

with open(os.path.join(ABS_PATH, 'config.yml'),  # type:ignore
            'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read()).get('postgresql_info', {})

USER = config.get('user')
PASSWORD = config.get('password')
DATABASE = config.get('database')
HOST = config.get('host')