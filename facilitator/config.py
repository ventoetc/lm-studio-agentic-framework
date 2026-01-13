"""
Configuration Loader
--------------------
Reads and validates facilitator.yaml.
"""

import yaml
import os

DEFAULT_CONFIG = {
    "agent_mode": {
        "enabled": False,
        "default_model": "local-model"
    },
    "phases": {
        "orientation": {
            "max_sentences": 4,
            "allow_lists": False
        },
        "execution": {
            "require_approval": True
        }
    },
    "agents": {
        "orientation": {
            "module": "agents.orientation",
            "class": "OrientationAgent"
        },
        "builder": {
            "module": "agents.builder",
            "class": "BuilderAgent"
        },
        "critic": {
            "module": "agents.critic",
            "class": "CriticAgent"
        }
    }
}

def load_config(config_path="facilitator.yaml"):
    """
    Loads configuration from YAML file with fallback to defaults.
    
    Args:
        config_path (str): Path to the config file.
        
    Returns:
        dict: The configuration dictionary.
    """
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Basic merge with defaults (shallow merge for top-level keys)
        # For a more robust solution, a deep merge would be better, 
        # but this suffices for the MVP.
        merged_config = DEFAULT_CONFIG.copy()
        if config:
            merged_config.update(config)
            
        return merged_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG
