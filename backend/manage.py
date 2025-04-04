#!/usr/bin/env python
"""
Django administrative tasks

This file is used to run administrative tasks for the Django project, such as management commands.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import os
import sys

# --------------------------------------------------------------------------------
# MAIN FUNCTION

def main() -> None:
    """
    Run administrative tasks using the Django management command line.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgpostman.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

# --------------------------------------------------------------------------------
# EXECUTION

if __name__ == '__main__':
    main()
