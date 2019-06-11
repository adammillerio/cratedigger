#!/usr/bin/env python3
from os.path import basename, splitext, join
from json import dumps
from typing import Iterable
from anytree import NodeMixin
from cratedigger.util.io import InputStream, OutputStream

class SeratoCrate(NodeMixin):
  # Delimiter for crates. The Serato crates directory is "flat" and Serato
  # uses the %% delimiter to determine when a crate is a "subcrate" of another
  delimiter = '%%'

  def __init__(self, parent = None, children = None) -> None:
    # "Version" of the crate, presumably something Serato determines
    self.version = '81.0'
    
    # Metadata to sort crate by, such as "song" for song name
    self.sort = 'song'

    # "Sort Rev"
    # TODO: Determine what this actually does and document it
    self.sort_rev = 256
    
    # All columns within the crate
    self.columns = ['song', 'artist', 'album', 'length']

    # All tracks within the crate
    self.tracks = []

    # anytree: Set parent and child nodes
    self.parent = parent
    if children:
      self.children = children
  
  def __str__(self) -> str:
    # Return only the name of the crate without the extension
    # and replace the delimiter with /
    return self.crate_name.replace(SeratoCrate.delimiter, '/')
  
  def to_json(self) -> str:
    # Return JSON serialized version of the crate
    return dumps(self.__dict__, indent=2, sort_keys=True)
  
  def load_crate(self, path: str) -> None:
    # Set crate path
    self.crate_name = splitext(basename(path))[0]

    # Open crate file as binary BufferedReader
    crate_file = open(path, 'rb')

    # Create InputStream helper from BufferedReader
    stream = InputStream(crate_file)

    # Header
    # Load the version
    stream.skip_string('vrsn')                                   # Skip vrsn
    stream.skip_bytes(b'\x00\x00')                               # Skip two empty byes after vrsn
    self.version = stream.read_string(8, 'utf-16-be')            # Set version from next 8 bytes as UTF-16 string
    stream.skip_string('/Serato ScratchLive Crate', 'utf-16-be') # Skip UTF-16 Big Endian (BE) junk string

    # Parse header sections until we reach the tracks (otrk) section
    # Get the first section
    while True:
      try:
        # Read the next section
        section = stream.read_string(4)
      except ValueError:
        # If the read didn't get 4 bytes, then we must be at the end of a crate
        # with no tracks, so just end the load here
        return
      
      if section == 'otrk':
        # If the section is otrk, it's time to start reading tracks
        break
      elif section == 'ovct':
        # Parse columns (ovct)
        # This pattern occurs once for every column
        # Example:
        # ovct\x00\x00\x00\x1atvcn\x00\x00\x00\x08\x00s\x00o\x00n\x00gtvcw\x00\x00\x00\x02\x000
        # ovct = 26 (0000001A)
        # tvcn = 8 (00000008)
        # column = 'song'
        # tvcw = 2 (0002)
        ovct = stream.read_int()                                   # Read ovct value
        stream.skip_string('tvcn')                                 # Skip tvcn
        tvcn = stream.read_int()                                   # Read tvcn value
        self.columns.append(stream.read_string(tvcn, 'utf-16-be')) # Decode UTF-16 string of tvcn length and append as column
        stream.skip_string('tvcw')                                 # Skip tvcw
        tvcw = stream.read_int()                                   # Read tvcw value
        stream.skip_bytes(b'\x00')                                 # Skip \x00
        stream.skip_string('0')                                    # Skip 0

        # Fail if ovct - tvcn is not 18
        difference = ovct - tvcn
        if difference != 18:
          raise ValueError('Expected (osrt - tvcn) to be 18, but found %d (osrt = %d, tvcn = %d)' % (difference, ovct, tvcn))
        
        # Fail if tvcw is not 2
        if tvcw != 2:
          raise ValueError('Expected tvcw to be 2, but found %d' % tvcw)
      elif section == 'osrt':
        # Parse sorting (osrt)
        # This pattern occurs only once
        # Example:
        # osrt\x00\x00\x00\x19tvcn\x00\x00\x00\x08\x00s\x00o\x00n\x00gbrev\x00\x00\x00\x01\x00
        # osrt = 25 (00000019)
        # tvcn = 8 (00000008)
        # sort = 'song'
        # sort_rev = 256
        osrt = stream.read_int()                          # Read osrt value
        stream.skip_string('tvcn')                        # Skip tvcn
        tvcn = stream.read_int()                          # Read tvcn value
        self.sort = stream.read_string(tvcn, 'utf-16-be') # Set sort key to UTF-16 string of tvcn length (e.g. song)
        stream.skip_string('brev')                        # Skip brev
        self.sort_rev = stream.read_int(5)                # Read next 5 bytes as sort rev

        # Fail of osrt - tvcn is not 17
        difference = osrt - tvcn
        if difference != 17:
          raise ValueError('Expected (osrt - tvcn) to be 17, but found %d (osrt = %d, tvcn = %d)' % (difference, osrt, tvcn))
      else:
        raise ValueError('Encountered unknown header section %s' % section)
    
    # Parse tracks
    # Example:
    # otrk\x00\x00\x00\x8aptrk\x00\x00\x00\x82\x00M\x00u\x00s\x00i\x00c\x00/
    # \x00F\x00L\x00A\x00C\x00/\x008\x00m\x00m\x00/\x008\x00m\x00m\x00 \x00-
    # \x00 \x00O\x00p\x00e\x00n\x00e\x00r\x00 \x00E\x00P\x00/\x000\x001\x00 
    # \x00-\x00 \x008\x00m\x00m\x00 \x00-\x00 \x00O\x00p\x00e\x00n\x00e\x00r
    # \x00 \x00E\x00P\x00 \x00-\x00 \x00O\x00p\x00e\x00n\x00e\x00r\x00.\x00f
    # \x00l\x00a\x00c
    # otrk = 138 (0000008A)
    # ptrk = 130 (00000082)
    # track = 'Music/FLAC/8mm/8mm - Opener EP/01 - 8mm - Opener EP - Opener.flac'
    first_track = True
    while True:
      if not first_track:
        # Skip otrk unless this is the first track
        # On the first track it was skipped during header parsing
        try:
          stream.skip_string('otrk')
        except ValueError:
          # If we got an exception, then this is the end of the file
          break
      
      first_track = False
      
      otrk = stream.read_int()   # Read otrk value
      stream.skip_string('ptrk') # Skip ptrk
      ptrk = stream.read_int()   # Read ptrk value

      difference = otrk - ptrk
      if difference != 8:
        raise ValueError('Expected (otrk - ptrk) to be 8, but found %d (otrk = %d, ptrk = %d)' % (difference, otrk, ptrk))
      
      # Read UTF-16 string of ptrk length to get track name and append it
      self.tracks.append(stream.read_string(ptrk, 'utf-16-be'))

    crate_file.close()
  
  def write_crate(self, path: str) -> None:
    # Open crate file as binary BufferedReader
    crate_file = open(join(path, '%s.crate' % self.crate_name), 'wb')

    # Create InputStream helper from BufferedReader
    stream = OutputStream(crate_file)

    # Header
    # Write the version
    stream.write_string('vrsn')                                   # Write vrsn
    stream.write_bytes(b'\x00\x00')                               # Write two empty bytes after vrsn
    stream.write_string(self.version, 'utf-16-be')                # Write version as UTF-16 string
    stream.write_string('/Serato ScratchLive Crate', 'utf-16-be') # Write junk as UTF-16 string
  
    # Write header sections
    # osrt
    sort_length = len(self.sort)                                  # Get length of sort word
    stream.write_string('osrt')                                   # Write osrt
    stream.write_int(sort_length * 2 + 17)                        # Write sort word length * 2 + 17 (arbitrary)
    stream.write_string('tvcn')                                   # Write tvcn
    stream.write_int(sort_length * 2)                             # Write sort word length * 2 (since UTF-16)
    stream.write_string(self.sort, 'utf-16-be')                   # Write sort word encoded as UTF-16
    stream.write_string('brev')                                   # Write brev
    stream.write_int(self.sort_rev, 5)                            # Write sort_rev as 5 bit int

    # Write columns
    for column in self.columns:                                   # For each column
      column_length = len(column)                                 # Get length of column word
      stream.write_string('ovct')                                 # Write ovct
      stream.write_int(column_length * 2 + 18)                    # Write column word length * 2 + 17 (arbitrary)
      stream.write_string('tvcn')                                 # Write tvcn
      stream.write_int(column_length * 2)                         # Write column word length * 2 (since UTF-16)
      stream.write_string(column, 'utf-16-be')                    # Write column word encoded as UTF-16
      stream.write_string('tvcw')                                 # Write tvcw
      stream.write_int(2)                                         # Write 2
      stream.write_bytes(b'\x00')                                 # Write \x00 byte
      stream.write_string('0')                                    # Write 0

    # Write tracks
    for track in self.tracks:                                     # For each track
      track_length = len(track)                                   # Get length of track word
      stream.write_string('otrk')                                 # Write otrk
      stream.write_int(track_length * 2 + 8)                      # Write track word length * 2 + 8 (arbitrary)
      stream.write_string('ptrk')                                 # Write ptrk
      stream.write_int(track_length * 2)                          # Write track word length * 2 (since UTF-16)
      stream.write_string(track, 'utf-16-be')                     # Write track word encoded as UTF-16
    
    # Close crate file
    crate_file.close()
