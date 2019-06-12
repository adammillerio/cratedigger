
#!/usr/bin/env python3
from _io import BufferedReader, BufferedWriter

class InputStream(object):
  """Utility class for interacting with a binary file.

  This class implements several methods to assist with seeking through an
  arbitrary binary file. This is used for loading Serato .crate files.

  """

  def __init__(self, reader: BufferedReader) -> None:
    """Initialize an Input Stream from a given file.

    This creates an InputStream for a given file.

    Args:
      reader (obj:`BufferedReader`): Open file to interact with

    """

    # Store read buffer
    self._stream = reader

  def read(self, length: int) -> bytes:
    """Read an arbitrary amount of bytes.

    Args:
      length (int): Amount of bytes to read

    Returns:
      read_bytes (bytes): Bytes read from file
    
    Raises:
      ValueError: If unable to read the specified number of bytes, typically due
                  to the end of the file being reached.

    """

    # Read amount of bytes equal to the provided content
    read = self._stream.read(length)
    read_length = len(read)

    if read_length != length:
      # If our read bytes is less than the read's length, raise an error
      # as the file is likely too short
      raise ValueError('Expected to read %d bytes but read only %d bytes' % (length, read_length))

    return read 

  def skip_string(self, skip_string: str, encoding: str = 'utf-8') -> None:
    """Skip a specified string in a binary file.

    This method attempts to skip a provided string within the buffered reader.

    Args:
      skip_string (str): String to skip
      encoding (str): Encoding of the string to skip within the binary file
    
    Raises:
      ValueError: If unable to skip the string, or if an unknown encoding is
                  specified.

    """

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
    """Skip a specified amount of bytes in a binary file.

    This method attempts to skip a provided set of bytes within the buffered
    reader.

    Args:
      skip_bytes (bytes): Bytes to skip
    
    Raises:
      ValueError: If unable to skip the specified bytes within the file

    """

    # Skip content
    read_bytes = self.read(len(skip_bytes))

    if skip_bytes != read_bytes:
      raise ValueError('Expected %s but got %s' % (str(skip_bytes), str(read_bytes)))

  def read_string(self, length: int, encoding: str = 'utf-8') -> str:
    """Read a string from a binary file.
    
    This method reads and decodes a given string from within the buffered reader

    Args:
      length (int): Length of bytes to read for the string
      encoding (str): Encoding to use when decoding the bytes to a string
    
    Returns:
      read_string (str): The decoded string

    """

    read = self.read(length)

    # Decode the bytes into a string and return
    return read.decode(encoding)
  
  def read_int(self, length: int = 4) -> int:
    """Read an integer from a binary file.

    This method reads a set amount of bytes from a file and returns the bytes
    represented as an int.

    Args:
      length (int, optional): Length of bytes to read for the int, defaults to
                              4 bytes (16-bit integer)
    
    Returns:
      read_int (int): The integer representation of the read bytes

    """

    # Read an integer of provided byte length and return it
    return int.from_bytes(self.read(length), byteorder='big')

class OutputStream(object):
  """Utility class for writing to a binary file.

  This class implements several methods to assist with writing an
  arbitrary binary file. This is used for writing Serato .crate files.


  """

  def __init__(self, writer: BufferedWriter) -> None:
    """Initialize an Output Stream from a given file.

    This creates an OutputStream for a given file.

    Args:
      writer (obj:`BufferedWriter`): Open file to interact with

    """

    # Store write buffer
    self._stream = writer
  
  def write_bytes(self, write_bytes: bytes) -> None:
    """Write an arbitrary amount of bytes.

    Args:
      write_bytes (bytes): Bytes to write

    """

    # Write the bytes provided
    self._stream.write(write_bytes)
  
  def write_string(self, write_string: str, encoding: str = 'utf-8') -> None:
    """Write an arbitrary string.

    Args:
      write_string (str): String to write
      encoding (str, optional): Encoding of the string, defaults to utf-8

    """

    # Encode the string and write it
    self._stream.write(write_string.encode(encoding))
  
  def write_int(self, write_int: int, length: int = 4) -> None:
    """Write an arbitrary int

    Args:
      write_int (int): Integer to write
      length (int): Number of bytes to use for representing the int

    """

    # Convert the int provided to bytes of provided length and write it
    self._stream.write(write_int.to_bytes(length, byteorder='big'))
