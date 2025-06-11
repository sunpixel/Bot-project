import configparser
import os
from pathlib import Path
from typing import List, Union

script_dir = os.path.dirname(os.path.abspath(__file__))
conf_path = os.path.abspath(os.path.join(script_dir, '..', 'config.ini'))

class ConfigManager:
    def __init__(self, config_path: str = conf_path):
        self.config = configparser.ConfigParser()
        self.config_path = config_path

        # Create default config if doesn't exist
        if not os.path.exists(config_path):
            self._create_default_config()

        self.config.read(config_path)

    def _create_default_config(self):
        """Create default configuration file"""
        self.config['database'] = {
            'path': '../../Data/DataBase/shop.db'
        }
        self.config['embeddings'] = {
            'model_name': 'all-MiniLM-L6-v2',
            'dimension': '384'
        }
        self.config['security'] = {
            'admin_ids': '',
            'secret_key': 'change-me-to-a-random-string'
        }
        self.config['api_keys'] = {
            'telegram': ''
        }
        self.config['logging'] = {
            'level': 'INFO',
            'file': 'app.log'
        }

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    @property
    def db_path(self) -> str:
        """Get resolved database path"""
        raw_path = self.config.get('database', 'path')
        return str(Path(__file__).parent.joinpath(raw_path).resolve())

    @property
    def model_name(self) -> str:
        return self.config.get('embeddings', 'model_name')

    @property
    def embedding_dimension(self) -> int:
        return self.config.getint('embeddings', 'dimension')

    @property
    def admin_ids(self) -> List[int]:
        ids = self.config.get('security', 'admin_ids')
        return [int(id.strip()) for id in ids.split(',') if id.strip()]

    @property
    def secret_key(self) -> str:
        return self.config.get('security', 'secret_key')

    def get_api_key(self, service: str) -> Union[str, None]:
        try:
            key = self.config.get('api_keys', service)
            return key if key else None
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None


# Singleton instance
config = ConfigManager()