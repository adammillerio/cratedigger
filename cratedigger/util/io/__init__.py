
#!/usr/bin/env python3
from _io import BufferedReader, BufferedWriter
from struct import unpack

class InputStream(object):
  def __init__(self, reader: BufferedReader) -> None:
    # Store read buffer
    self._stream = reader

  def read(self, length: int) -> bytes:
    # Read amount of bytes equal to the provided content
    read = self._stream.read(length)
    read_length = len(read)

    if read_length != length:
      # If our read bytes is less than the read's length, raise an error
      # as the file is likely too short
      raise ValueError('Expected to read %d bytes but read only %d bytes' % (length, read_length))

    return read 

  def skip_string(self, skip_string: str, encoding: str = 'utf-8') -> None:
    if encoding == 'utf-16-be':
      # Since python uses UTF-8 strings, we need to multiply the length of bytes
      # by two when dealing with UTF-16
      length = len(skip_string) * 2
    elif encoding == 'utf-8':
      length = len(skip_string)
    else:
      raise ValueError('Unknown string encoding type %s' % encoding)

    # Skip content
    read = self.read(length)

    # Decode the bytes into a string
    read_string = read.decode(encoding)

    if skip_string != read_string:
      # If our strings are not equal, indicate skip failure
      raise ValueError('Expected %s but got %s' % (skip_string, read_string))

  def skip_bytes(self, skip_bytes: bytes) -> None:
    # Skip content
    read_bytes = self.read(len(skip_bytes))

    if skip_bytes != read_bytes:
      raise ValueError('Expected %s but got %s' % (str(skip_bytes), str(read_bytes)))

  def read_string(self, length: int, encoding: str = 'utf-8') -> str:
    read = self.read(length)

    # Decode the bytes into a string and return
    return read.decode(encoding)
  
  def read_int(self, length: int = 4) -> int:
    # Read an integer of provided byte length and return it
    return int.from_bytes(self.read(length), byteorder='big')

class OutputStream(object):
  def __init__(self, writer: BufferedWriter) -> None:
    # Store write buffer
    self._stream = writer
  
  def write_bytes(self, write_bytes: bytes) -> None:
    # Write the bytes provided
    self._stream.write(write_bytes)
  
  def write_string(self, write_string: str, encoding: str = 'utf-8') -> None:
    # Encode the string and write it
    self._stream.write(write_string.encode(encoding))
  
  def write_int(self, write_int: int, length: int = 4) -> None:
    # Convert the int provided to bytes of provided length and write it
    self._stream.write(write_int.to_bytes(length, byteorder='big'))
