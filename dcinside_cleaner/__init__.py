from .cli.cleaner_console import Console
from .gui.cleaner_gui import execute

RUNNING_MODE = 'gui' # 'gui' | 'cli'

def main():
    if RUNNING_MODE == 'cli':
        Console()

    if RUNNING_MODE == 'gui':
        execute()

__all__ = ['main', 'dcinside_cleaner', 'proxy_checker', 'cli', 'gui']