#!/usr/bin/env python3
import logging
import click
from cratedigger.media.library import MediaLibrary
from cratedigger.util.context import Context
from cratedigger.cli import pass_context

logger = logging.getLogger(__name__)

@click.command('sync', short_help='Run a sync operation')
@click.option('--library-dir', type=click.Path(exists=True, file_okay=False, resolve_path=False), required=True, help='Folder containing music library')
@click.option('--serato-dir', type=click.Path(exists=True, file_okay=False, resolve_path=False), help='Folder containing _Serato_ directory, defaults to drive/volume that music library is on')
@pass_context
def cli(ctx: Context, library_dir: str, serato_dir: str) -> None:
  logger.info('Loading media library from %s' % library_dir)

  # Read media library
  media_library = MediaLibrary()
  media_library.load(library_dir)

  logger.info('Loaded %d media library crates' % len(media_library))

  if serato_dir is not None:
    # Override crates_path if --serato-dir provided
    logger.info('Overriding Serato directory to %s' % serato_dir)
    media_library.crates_path = serato_dir

  if ctx.verbose:
    # Print rendered tree of library
    logger.debug('Rendering media library tree')
    logger.debug('\n%s' % media_library.render())
  
  # Write the library crates 
  if not ctx.dry_run:
    logger.info('Writing media library crates to %s' % media_library.crates_path)
    media_library.write()
  else:
    logger.info('Writing media library crates to %s (Dry Run)' % media_library.crates_path)
