# oneclicksetup/env_utils.py

import os
import platform
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables from a .env file if present.
    This function is called once at startup (in cli.py).
    """
    load_dotenv()  # This will parse a .env file if it exists in the current directory or parent
    # Example: if you want to read them right away:
    # MY_VAR = os.getenv("MY_VAR", "default_value")
    # print(f"MY_VAR is {MY_VAR}")
    pass

def detect_platform():
    """
    Returns a string like 'linux', 'macos', or 'windows'
    based on the OS platform.
    """
    current = platform.system().lower()
    if 'linux' in current:
        return 'linux'
    elif 'darwin' in current:
        return 'macos'
    elif 'windows' in current:
        return 'windows'
    else:
        return 'unknown'
