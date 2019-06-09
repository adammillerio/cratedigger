#!/usr/bin/env python3
import click
from cratedigger.serato.library import SeratoLibrary
from cratedigger.util.context import Context
from cratedigger.cli import pass_context

@click.command('sync', short_help='Run a sync operation')
@click.option('--library-dir', type=click.Path(exists=True, file_okay=False, resolve_path=False), required=True, help='Folder containing music library')
@click.option('--serato-dir', type=click.Path(exists=True, file_okay=False, resolve_path=False), help='Folder containing _Serato_ directory, defaults to drive/volume that music librar is on')
@pass_context
def cli(ctx: Context, library_dir: str, serato_dir: str) -> None:
  # TODO: Implement handling of no serato dir provided
  if serato_dir == None:
    pass
  
  # Read and write library
  library = SeratoLibrary(serato_dir)
  library.write_library()
