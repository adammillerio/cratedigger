#!/usr/bin/env python3
import os
from glob import glob
from re import match
from json import dumps
from typing import List
from anytree import PreOrderIter
from cratedigger.serato.crate import SeratoCrate

class SeratoLibrary(object):
  def __init__(self, path: str) -> None:
    # Delimiter for crates. The Serato crates directory is "flat" and Serato
    # uses the %% delimiter to determine when a crate is a "subcrate" of another
    self.delimiter = '%%'

    # Store path
    self.path = path
    
    # Create the root node for the crates tree
    self.crates = SeratoCrate(path=None, parent=None)

    # Load Serato crates
    self.load_library(path)
  
  def __str__(self) -> str:
    # Return serialized JSON representation
    return dumps(self.__dict__, indent=2, sort_keys=True, default=to_dict)
  
  def load_library(self, path: str) -> None:
    # Build the path to Serato crates
    self.crates_path = os.path.join(path, '_Serato_', 'Subcrates')

    if not os.path.isdir(self.crates_path):
      # Error if there is no serato library here
      raise ValueError('No _Serato_ folder present in %s' % path)
    
    # Get a list of all .crate files, with only their basenames and no path
    crates = [os.path.basename(file) for file in glob(os.path.join(self.crates_path, '*.crate'))]

    # Start loading all "base" (not delimiters) crates
    for crate in [crate for crate in crates if not self.delimiter in crate]:
      # Create child node from the base crate
      child = SeratoCrate(os.path.join(self.crates_path, crate), parent=self.crates)

      # Split the .crate extension and add the delimiter
      # e.g. '8mm%%' for '8mm.crate'
      prefix = '%s%s' % (os.path.splitext(os.path.basename(crate))[0], self.delimiter)

      # Find all "subcrates" that start with this prefix and load them
      # under the child node
      subcrates = [crate for crate in crates if crate.startswith(prefix)]
      if len(subcrates) != 0:
        self.load_crates(subcrates, prefix, child)
    
    # Determine volume name and type
    self.split_volume(path)
  
  def load_crates(self, crates: List[str], prefix: str, parent: SeratoCrate) -> None:
    for crate in crates:
      # Create child node from the crate, using the provided parent
      child = SeratoCrate(os.path.join(self.crates_path, crate), parent=parent)

      # Split the .crate extension and add the delimiter
      # e.g. '8mm%%8mm - Opener EP%%' for '8mm%%8mm - Opener EP.crate'
      prefix = '%s%%' % os.path.splitext(os.path.basename(crate))[0]

      # Find all "subcrates" that start with this new prefix and load them
      # under the new child node
      subcrates = [crate for crate in crates if crate.startswith(prefix)]
      if len(subcrates) != 0:
        self.load_crates(subcrates, prefix, child)
  
  def write_library(self) -> None:
    for crate in PreOrderIter(self.crates):
      # Traverse the tree and write all crates
      crate.write_crate()
  
  def split_volume(self, path: str) -> None:
    # Match a mac volume type if the path starts with /Volumes/*
    volume_regex = match(r'(^\/Volumes\/)([^\/]+)', path)
    if volume_regex:
      # Set volume type to mac and get volume name
      # e.g. serato for /Volumes/serato
      self.volume_type = 'mac'
      self.volume = volume_regex.groups()[1]
      return

    # Match a windows volume type if the path starts with *:\\
    volume_regex = match(r'(^[a-zA-Z])(:\\\\)', path) 
    if volume_regex:
      # Set volume type to windows and get volume name
      # e.g. c for C:\\serato
      self.volume_type = 'windows'
      self.volume = volume_regex.groups()[0].lower()
      return
    
    # Serato doesn't support other platforms, and won't find any other library
    # locations, so error out
    raise ValueError('Cannot determine volume type for "%s"')

def to_dict(obj) -> dict:
  return obj.__dict__
