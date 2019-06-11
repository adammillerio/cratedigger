#!/usr/bin/env python3
import click
from anytree import RenderTree
from cratedigger.media.library import MediaLibrary
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
  
  # Read and write media library
  media_library = MediaLibrary()
  media_library.load(library_dir)
  media_library.render()
  media_library.write()
  
  # Read and write serato library
  serato_library = SeratoLibrary()
  serato_library.load(serato_dir)
  serato_library.render()
  serato_library.write()
