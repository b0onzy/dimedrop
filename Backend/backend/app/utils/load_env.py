#!/usr/bin/env python3
"""
Environment Variable Loader for DimeDrop
Loads variables from both ~/.env and Backend/config/.env with expansion support
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables in the correct order:
    1. Load from ~/.env (global secrets)
    2. Load from Backend/config/.env (project-specific overrides)

    This allows sensitive API keys to be stored in ~/.env
    while project-specific config stays in the repo.
    """

    # Load from home directory first (global secrets)
    home_env = Path.home() / '.env'
    if home_env.exists():
        print(f"✅ Loading global secrets from {home_env}")
        load_dotenv(home_env, override=False, interpolate=True)
    else:
        print(f"⚠️  No global .env found at {home_env}")

    # Load from project root .env (project-specific variables)
    project_root_env = Path(__file__).parents[4] / '.env'
    if project_root_env.exists():
        print(f"✅ Loading project root config from {project_root_env}")
        load_dotenv(project_root_env, override=True, interpolate=True)
    else:
        print(f"⚠️  No project root .env found at {project_root_env}")

    # Load from project directory (allows overrides)
    project_env = Path(__file__).parent / 'config' / '.env'
    if project_env.exists():
        print(f"✅ Loading project config from {project_env}")
        load_dotenv(project_env, override=True, interpolate=True)
    else:
        print(f"⚠️  No project .env found at {project_env}")

    # Verify critical variables
    critical_vars = [
        'EBAY_APP_ID',
        'SUPABASE_URL',
        'AUTH0_DOMAIN'
    ]

    missing = []
    for var in critical_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}"
        print(f"\n❌ {error_msg}")
        raise ValueError(error_msg)

    return len(missing) == 0


if __name__ == '__main__':
    # Test the loader
    print("\n=== DimeDrop Environment Loader ===\n")
    success = load_environment()

    print("\n=== Loaded Variables ===\n")

    # Display non-sensitive vars
    for key in ['EBAY_APP_ID', 'DATABASE_URL', 'SUPABASE_URL']:
        value = os.getenv(key)
        if value:
            # Mask sensitive parts
            if 'key' in key.lower() or 'secret' in key.lower():
                display = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display = value
            print(f"  {key}: {display}")
        else:
            print(f"  {key}: (not set)")

    print("\n" + ("✅ All critical variables loaded!" if success else "⚠️  Some variables are missing"))
