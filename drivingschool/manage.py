#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_driving_school.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        print("Erreur : impossible d'importer Django.", file=sys.stderr)
        sys.exit(84)
    except Exception as e:
        print(f"Erreur inattendue : {e}", file=sys.stderr)
        sys.exit(84)

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Erreur d'exécution Django : {e}", file=sys.stderr)
        sys.exit(84)

if __name__ == '__main__':
    main()
