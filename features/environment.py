import os
import sys
from pathlib import Path
import django
from django.core.management import call_command

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
django.setup()


def before_all(context):
    call_command("migrate", "--run-syncdb", verbosity=0)

