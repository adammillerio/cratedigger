#!/usr/bin/env python3
import os
from json import dumps
from cratedigger.media.crate import MediaCrate
from cratedigger.serato.library import SeratoLibrary

class MediaLibrary(SeratoLibrary):
  root_crate = MediaCrate(parent=SeratoLibrary.root_crate)
  root_crate.crate_name = 'Media'

  def __init__(self) -> None:
    super().__init__()
  
  def load(self, path: str) -> None:
    # Store the path
    self.path = path

    # Determine volume name and type
    self.split_volume(path)

    # Add Media root crate to the global tree
    self.crates = MediaCrate(parent=MediaLibrary.root_crate)
    self.crates.crate_name = self.volume

    # Load crates
    self.load_crates(path, self.crates)

  def load_crates(self, path: str, parent: MediaCrate) -> None:
    # Create new subcrate and load it
    child = MediaCrate(parent=parent)
    child.load_crate(path, self.volume, self.volume_path)

    for file in os.listdir(path):
      # If this crate has subdirectories, load the subcrates
      full_path = os.path.join(path, file)

      if os.path.isdir(full_path):
        self.load_crates(full_path, child)
