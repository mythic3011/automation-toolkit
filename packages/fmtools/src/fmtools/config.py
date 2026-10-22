"""
Configuration management for fmtools.
"""

import yaml
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional
from .utils import get_config_dir


DEFAULT_CONFIG = {
    'defaults': {
        'dedup': {
            'algorithm': 'sha256',
            'keep': 'newest',
            'min_size': 0,
        },
        'organize': {
            'mode': 'type',
            'categories': None,
        },
        'rename': {
            'padding': 3,
            'start': 1,
        },
    },
    'rust': {
        'auto_use': True,
        'threshold': 1000,  # files
    },
    'logging': {
        'level': 'INFO',
        'file': None,
    },
}


class Config:
    """Configuration manager for fmtools."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration."""
        self.config_dir = get_config_dir()
        
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = self.config_dir / 'config.yaml'
        
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            # Create default config
            self.save(DEFAULT_CONFIG)
            return deepcopy(DEFAULT_CONFIG)
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = yaml.safe_load(f) or {}
            
            # Merge with defaults (defaults for missing keys)
            config = self._merge_configs(DEFAULT_CONFIG, loaded_config)
            return config
        
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
            print("Using default configuration")
            return deepcopy(DEFAULT_CONFIG)
    
    def save(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_file}: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Example: config.get('defaults.dedup.algorithm')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set a configuration value using dot notation.
        
        Example: config.set('defaults.dedup.algorithm', 'md5')
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save()
    
    def show(self) -> str:
        """Return configuration as formatted YAML string."""
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False)
    
    def reset(self):
        """Reset configuration to defaults."""
        self.config = deepcopy(DEFAULT_CONFIG)
        self.save()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults."""
        result = deepcopy(default)
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_log_file(self, tool_name: Optional[str] = None) -> Optional[Path]:
        """Get log file path for a tool."""
        log_file = self.get('logging.file')
        
        if log_file:
            log_path = Path(log_file)
            if tool_name and not log_path.suffix:
                # If log_file is a directory, create tool-specific log
                return log_path / f"{tool_name}.log"
            return log_path
        
        # Default: tool-specific log in config dir
        if tool_name:
            return self.config_dir / f"{tool_name}.log"
        
        return None

