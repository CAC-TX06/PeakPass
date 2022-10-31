import os
from pathlib import Path
import yaml

os.chdir(Path(__file__).parent.parent)
ABS_PATH = Path(os.getcwd())

with open(os.path.join(ABS_PATH, 'config.yml'),  # type:ignore
            'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read()).get('postgresql_info', {})

username = config.get('username')
password = config.get('password')
host = config.get('host')
port = config.get('port')
database = config.get('database')
sslmode = config.get('sslmode')

CONNECTION_STRING = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={sslmode}"
SECRET_KEY = config.get('secret_key')