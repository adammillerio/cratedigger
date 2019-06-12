#!/usr/bin/env python3
import os
from logging import getLogger
from json import dumps
from typing import Tuple, TypeVar, Type
from os.path import splitext, basename
from anytree import NodeMixin
from cratedigger.serato.crate import SeratoCrate

# Logging
logger = getLogger(__name__)

# All file types officially supported by Serato
# https://support.serato.com/hc/en-us/articles/204177974-Serato-DJ-Pro-Supported-File-Types
SUPPORTED_FILE_TYPES = (
  '.mp3',
  '.ogg',
  '.alac',
  '.flac',
  '.aif',
  '.wav',
  '.wl.mp3',
  '.mp4',
  '.m4a',
  '.aac'
)

# Type var
MC = TypeVar('MC', bound='MediaCrate')

class MediaCrate(SeratoCrate):
  """A media folder represented as a Serato Crate.

  This class is intended to read a given media folder and represent it as a
  Serato Crate.

  """

  def __init__(self, parent: Type[MC] = None, children: Tuple[Type[MC]] = None) -> None:
    """Initialize a Media Crate

    This method invokes the SeratoCrate constructor in order to set the provided
    parent node and children.

    Args:
      parent (:obj:`MediaCrate`, optional): Parent crate (if subcrate)
      children (:obj:`tuple` of obj:`MediaCrate`, optional): Child crates

    """

    super().__init__(parent, children)

  def load_crate(self, path: str, volume: str, volume_path: str, prefix: str = None) -> None:
    """Load a given media folder path as a Serato crate.

    This method lists a given directory, and adds all compatible files to the
    Serato crate as tracks.    

    Args:
      path (str): Path to load tracks from
      volume (str): Volume that the tracks are being loaded from, used in the
                    crate name
      volume_path (str): Root path on the volume that tracks are being loaded,
                         used when converting track paths to the Serato
                         "relative" format
      prefix (str, optional): Prefix to append to the crate name

    """

    logger.debug('Loading Media crate from %s' % path)

    # Add prefix to crate name if provided
    if prefix is not None:
      prefix = prefix + SeratoCrate.delimiter
    else:
      prefix = ''

    # Remove the volume from the path, as it is relative in Serato
    self.crate_path = path[path.startswith(volume_path) and len(volume_path):]

    # Assemble the crate name
    # This leverages both the "root crate" for media libraries, as well as
    # the volume name to ensure that there is no collission between different
    # volumes if this tool is ran against multiple volumes
    # Example
    # Path: C:\Music\8mm\8mm - Opener EP
    # Name: Media%%C%%Music%%8mm%%8mm - Opener EP
    self.crate_name = '%s%s%s%s' % (
      prefix, volume, SeratoCrate.delimiter,
      self.crate_path.replace('/', SeratoCrate.delimiter).replace('\\', SeratoCrate.delimiter)
    )

    for file in os.listdir(path):
      if file.endswith(SUPPORTED_FILE_TYPES):
        self.tracks.append(os.path.join(self.crate_path, file).replace('\\', '/'))
