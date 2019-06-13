#!/usr/bin/env python3
import os
from pathlib import Path
from logging import getLogger
from glob import glob
from re import match
from json import dumps
from typing import List
from anytree import PreOrderIter, RenderTree
from cratedigger.util import to_dict
from cratedigger.serato.crate import SeratoCrate

# Logging
logger = getLogger(__name__)

class SeratoLibrary(object):
  """A library of Serato Crates.

  This represents a library within Serato. This is composed of a volume and
  associated metadata, as well as a list of crates present on that volume.

  Attributes:
    path (str): Path to the loaded Serato Library
    volume_type (str): Type of the volume, either mac or windows
    volume (str): Name of the volume. On windows, this is a drive letter. On a
                  mac, this is either root if on the root drive, or an arbitrary
                  volume name if on a volume.
    volume_path (str): Path to the root of the volume
    crates_path (str): Path to the Subcrates folder on the volume
    crates (obj:`SeratoCrate`): Tree of all crates in the Serato Library
    root_crate (obj:`SeratoCrate`): Root crate of tree, all loaded Serato
                                    libraries are grouped under this

  """
  
  # "Root" crate of the crates tree, all crates are grouped under this
  root_crate = SeratoCrate(parent=None)
  root_crate.crate_name = 'Root'

  def __init__(self) -> None:
    """Initialize a Serato Library

    This initializes the Serato Library and it's attributes to default values.

    """

    self.path = ''
    self.volume_type = ''
    self.volume = ''
    self.volume_path = ''
    self.crates_path = ''

    pass
  
  def __str__(self) -> str:
    """Return a string representation of the Serato Library.

    This returns the Serato Library object serialized as JSON.

    Returns:
      library_str (str): String representation of the Serato Library

    """

    # Return serialized JSON representation
    return dumps(self.__dict__, indent=2, sort_keys=True, default=to_dict)
  
  def __len__(self) -> int:
    """Return the length of a Serato Library

    This returns the count of all decendant crates in the Serato Library's tree.

    Returns:
      length (int): Length of the Serato Library

    """

    # Return the amount of descendants in the crates tree
    return len(self.crates.descendants)
  
  def render(self) -> str:
    """Render the Serato Library as an ASCII tree.
    
    This renders all crates within the Serato Library and returns this
    representation in string format.

    Returns:
      tree (str): String representation of the Serato Library tree

    """

    # String for rendered representation
    render = ''

    # Render a tree of all crates
    for pre, _, node in RenderTree(self.crates):
      render += '%s%s\n' % (pre, node)
    
    # Return rendered string
    return render
  
  def load(self, path: str) -> None:
    """Load a Serato Library from a given path

    This method loads all .crate files in a given path's Subcrates folder
    as SeratoCrate objects and assembles them in a tree structure based on 
    their delimiters.

    Args:
      path (str): Path to the _Serato_ folder

    Raises:
      ValueError: If no _Serato_ folder is present in the given path

    """

    # Store the path
    self.path = path
    
    # Determine volume name and type
    self.split_volume(path)

    # SeratoLibrary loads from the root, so set crates to the root
    self.crates = SeratoLibrary.root_crate

    if not os.path.isdir(self.crates_path):
      # Error if there is no serato library here
      raise ValueError('No _Serato_ folder present in %s' % path)

    # Get a list of all .crate files, with only their basenames and no path
    crates = [os.path.basename(file) for file in glob(os.path.join(self.crates_path, '*.crate'))]

    # Start loading all "base" (not delimiters) crates
    for crate in [crate for crate in crates if crate.startswith('%s%%' % SeratoLibrary.root_crate.crate_name)]:
      # Create child node from the base crate
      child = SeratoCrate(parent=self.crates)
      child.load_crate(os.path.join(self.crates_path, crate))

      # Split the .crate extension and add the delimiter
      # e.g. '8mm%%' for '8mm.crate'
      prefix = '%s%s' % (os.path.splitext(os.path.basename(crate))[0], SeratoCrate.delimiter)

      # Find all "subcrates" that start with this prefix and load them
      # under the child node
      subcrates = [crate for crate in crates if crate.startswith(prefix)]
      if len(subcrates) != 0:
        self.load_crates(subcrates, prefix, child)
  
  def load_crates(self, crates: List[str], prefix: str, parent: SeratoCrate) -> None:
    """Recursively load a set of Serato .crate files.

    This method takes a list of crates, and loads them as children of a given
    SeratoCrate. If any of these crates have their own subcrates, this method
    is recursively called until the end of the tree is reached.

    Args:
      crates (obj:`list` of obj:`str`): List of paths to .crate files
      prefix (str): The prefix to use when attempting to locate subcrates
      parent (obj:`SeratoCrate`): Parent crate of the subcrates to be loaded

    """

    for crate in crates:
      # Create child node from the crate, using the provided parent
      child = SeratoCrate(parent=parent)
      child.load_crate(os.path.join(self.crates_path, crate))

      # Split the .crate extension and add the delimiter
      # e.g. '8mm%%8mm - Opener EP%%' for '8mm%%8mm - Opener EP.crate'
      prefix = '%s%%' % os.path.splitext(os.path.basename(crate))[0]

      # Find all "subcrates" that start with this new prefix and load them
      # under the new child node
      subcrates = [crate for crate in crates if crate.startswith(prefix)]
      if len(subcrates) != 0:
        self.load_crates(subcrates, prefix, child)
  
  def write(self) -> None:
    """Write all crates in a Serato Library as .crate files.

    This method traverses the Serato Library and writes all Serato Crates as
    .crate files in the crates_path.

    """

    if not os.path.exists(self.crates_path):
      # Create the crates path if it doesn't exist
      logger.info('Creating crates directory %s' % self.crates_path )
      os.makedirs(self.crates_path)

    for crate in PreOrderIter(self.crates):
      # Traverse the tree and write all crates
      crate.write_crate(self.crates_path)
  
  def split_volume(self, path: str) -> None:
    """Determine volume metadata of the library based on a given path.

    This method takes a given path and determines the associated volume
    metadata.

    Args:
      path (str): Path to determine volume metadata from

    Raises:
      ValueError: If the volume type of the path cannot be determined

    """

    # Match a mac volume type if the path starts with /Volumes/*
    volume_regex = match(r'(^\/Volumes\/)([^\/]+)', path)
    if volume_regex:
      # Set volume type to mac and get volume name
      # e.g. serato for /Volumes/serato
      self.volume_type = 'mac'
      self.volume = volume_regex.groups()[1]
      self.volume_path = '/Volumes/%s/' % self.volume

      # Set crates path to /Volumes/volume/_Serato_/Subcrates
      self.crates_path = os.path.join(self.volume_path, '_Serato_', 'Subcrates')      

      return
    
    # Also match a mac volume type if the path starts with /Users/*
    volume_regex = match(r'(^\/Users\/)([^\/]+)', path)
    if volume_regex:
      # Set volume type to mac and set the volume path to root
      self.volume_type = 'mac'
      self.volume = 'root'
      self.volume_path = '/'

      # Set crates path to ~/Music/_Serato_/Subcrates
      # This is where the crates on the root drive always live on Mac
      self.crates_path = os.path.join(Path.home(), 'Music', '_Serato_', 'Subcrates')      

      return

    # Match a windows volume type if the path starts with *:\\
    volume_regex = match(r'(^[a-zA-Z])(:\\)', path)
    if volume_regex:
      # Set volume type to windows and get volume name
      # e.g. c for C:\\serato
      self.volume_type = 'windows'
      self.volume = volume_regex.groups()[0].upper()
      self.volume_path = '%s:\\' % self.volume

      if self.volume == 'C':
        # Set crates path to C:\Users\user\Music\_Serato_\Subcrates if C drive
        # This is where the crates for the C drive always live on Windows
        self.crates_path = os.path.join(Path.home(), 'Music', '_Serato_', 'Subcrates')
      else:
        # Set crates path to volume:\_Serato_\Subcrates otherwise
        self.crates_path = os.path.join(self.volume_path, '_Serato_', 'Subcrates')
      
      return
    
    # Serato doesn't support other platforms, and won't find any other library
    # locations, so error out
    raise ValueError('Cannot determine volume type for "%s"')
