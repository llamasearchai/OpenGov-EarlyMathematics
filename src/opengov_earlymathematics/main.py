#!/usr/bin/env python3
"""Main entry point for OpenGov Early Mathematics platform."""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from opengov_earlymathematics.ui.app import app

    app()
except ImportError as e:
    print(f"Error importing application: {e}")
    print("Please ensure all dependencies are installed with: uv sync")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nGoodbye! 👋")
    sys.exit(0)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
