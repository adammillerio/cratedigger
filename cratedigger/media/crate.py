#!/usr/bin/env python3
import os
from json import dumps
from os.path import splitext, basename
from anytree import NodeMixin
from cratedigger.serato.crate import SeratoCrate

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
  # The "root crate" for crates derived from a media library
  root_crate = 'Media'

  def __init__(self, parent = None, children = None) -> None:
    super().__init__(parent, children)

  def load_crate(self, path: str, volume_path: str) -> None:
    self.crate_path = path[path.startswith(volume_path) and len(volume_path):]
    self.crate_name = '%s%s%s' % (
      MediaCrate.root_crate, SeratoCrate.delimiter, 
      self.crate_path.replace('/', SeratoCrate.delimiter)
    )

    for file in os.listdir(path):
      if file.endswith(SUPPORTED_FILE_TYPES):
        self.tracks.append(os.path.join(self.crate_path, file))
