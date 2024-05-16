# test pyton script

print('*'*20)
print('|'+' '*18+'|')
print('|'+f'{"Hello, World!": ^18}'+'|')
print('|'+' '*18+'|')
print('*'*20)

import pip
print(f'pip ver {pip.__version__}')

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package, '--user'])
    else:
        pip._internal.main(['install', package, '--user'])

# install('rich')

import rich
print(f'rich : {rich}')

# from rich import print
# from rich.console import Console
# from rich.progress import track
# from time import sleep

# # Initialize a console
# console = Console()

# # Print a simple colored message
# print("[bold magenta]Rich[/bold magenta] makes your CLI more [bold green]beautiful![/bold green]")

# # Print a table
# from rich.table import Table

# table = Table(title="Favorite Colors")

# table.add_column("Name", justify="right", style="cyan", no_wrap=True)
# table.add_column("Color", style="magenta")
# table.add_row("Jake", "Yellow")
# table.add_row("John", "Blue")
# table.add_row("Sarah", "Red")

# console.print(table)