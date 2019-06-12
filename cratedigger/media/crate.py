#!/usr/bin/env python3
import os
from logging import getLogger
from json import dumps
from os.path import splitext, basename
from anytree import NodeMixin
from cratedigger.media.library import MediaLibrary
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

class MediaCrate(SeratoCrate):
  def __init__(self, parent = None, children = None) -> None:
    super().__init__(parent, children)

  def load_crate(self, path: str, volume: str, volume_path: str) -> None:
    logger.debug('Loading Media crate from %s' % path)

    # Remove the volume from the path, as it is relative in Serato
    self.crate_path = path[path.startswith(volume_path) and len(volume_path):]

    # Assemble the crate name
    # This leverages both the "root crate" for media libraries, as well as
    # the volume name to ensure that there is no collission between different
    # volumes if this tool is ran against multiple volumes
    # Example
    # Path: C:\Music\8mm\8mm - Opener EP
    # Name: Media%%C%%Music%%8mm%%8mm - Opener EP
    self.crate_name = '%s%s%s%s%s' % (
      MediaLibrary.root_crate.crate_name, SeratoCrate.delimiter,
      volume, SeratoCrate.delimiter,
      self.crate_path.replace('/', SeratoCrate.delimiter).replace('\\', SeratoCrate.delimiter)
    )

    for file in os.listdir(path):
      if file.endswith(SUPPORTED_FILE_TYPES):
        self.tracks.append(os.path.join(self.crate_path, file).replace('\\', '/'))
