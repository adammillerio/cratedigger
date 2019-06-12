#!/usr/bin/env python3
import os
from json import dumps
from cratedigger.media.crate import MediaCrate
from cratedigger.serato.library import SeratoLibrary

class MediaLibrary(SeratoLibrary):
  """A library of media folders represented as Serato crates.

  This is composed of a volume and associated metadata, as well as a list of
  folders and their equivalent Serato crate representation.

  Attributes:
    path (str): Path to the loaded Serato Library
    volume_type (str): Type of the volume, either mac or windows
    volume (str): Name of the volume. On windows, this is a drive letter. On a
                  mac, this is either root if on the root drive, or an arbitrary
                  volume name if on a volume.
    volume_path (str): Path to the root of the volume
    crates_path (str): Path to the Subcrates folder on the volume
    crates (obj:`MediaCrate`): Tree of all crates in the Serato library
    root_crate (obj:`MediaCrate`): Root crate of this folder's tree, all loaded
                                   Serato libraries are grouped under this

  """

  root_crate = MediaCrate(parent=SeratoLibrary.root_crate)
  root_crate.crate_name = 'Media'

  def __init__(self) -> None:
    """Initialize a Media Library.

    This invokes the initialization method for the Serato Library.

    """

    super().__init__()
  
  def load(self, path: str) -> None:
    """Load a Media Library from a given path.

    This method traverses all folders in a given path and creates Media crates
    with all compatible files.

    Args:
      path (str): Path to load crates for.

    """

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
    """Load crates in a given media folder.

    This creates a MediaCrate for a given path and parent, and loads all
    compatible files into it. Then, if there are any subdirectories, it
    recursively invokes this method to load the subcrates.

    Args:
      path (str): Path to load a crate from
      parent (obj:`MediaCrate`): Parent MediaCrate for the created subcrate

    """
    
    # Create new subcrate and load it
    child = MediaCrate(parent=parent)
    child.load_crate(path, self.volume, self.volume_path, MediaLibrary.root_crate.crate_name)

    for file in os.listdir(path):
      # If this crate has subdirectories, load the subcrates
      full_path = os.path.join(path, file)

      if os.path.isdir(full_path):
        self.load_crates(full_path, child)
