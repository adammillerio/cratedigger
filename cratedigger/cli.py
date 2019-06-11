#!/usr/bin/env python3
import os
import sys
import logging
import click
from typing import List, Any
from cratedigger.util.context import Context

# Logging
logger = logging.getLogger(__name__)

# Load env vars prefixed with CRATEDIGGER
CONTEXT_SETTINGS = dict(auto_envvar_prefix='CRATEDIGGER')

# Function decorator to pass the global CLI context into a function
pass_context = click.make_pass_decorator(Context, ensure=True)

# Command folder, containing all Click CLI commands
# cratedigger/commands
command_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))

class CrateDigger(click.MultiCommand):
  def list_commands(self, ctx: Context) -> List[str]:
    # Commands array
    commands = []

    for filename in os.listdir(command_folder):
      # Append each filename in the command folder to the list, without .py
      # e.g. sync for sync.py
      if filename.endswith('.py'):
        commands.append(filename[:-3])
    
    # Return sorted list of all commands
    commands.sort()
    return commands

  def get_command(self, ctx: Context, name: str) -> Any:
    # Attempt to load the command
    try:
      # Python 2 compatability
      if sys.version_info[0] == 2:
        name = name.encode('ascii', 'replace')
      
      # Import the command file's cli function
      mod = __import__('cratedigger.commands.' + name, None, None, ['cli'])
    except ImportError:
      # Return nothing if unable to import
      return
    
    # Return the cli function
    return mod.cli

@click.command(cls=CrateDigger, context_settings=CONTEXT_SETTINGS)
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--dry-run', is_flag=True, help='Print all actions to console without applying')
@pass_context
def cli(ctx: Context, verbose: bool, dry_run: bool) -> None:
  # Set context values
  ctx.verbose = verbose
  ctx.dry_run = dry_run

  # Set log level
  if verbose:
    level = logging.DEBUG
  else:
    level = logging.INFO
  
  # Initialize logger
  logging.basicConfig(level=level)
