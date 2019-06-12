#!/usr/bin/env python3

class Context(object):
  """Click CLI context class.

  This class is used to share data from the Click CLI within the cratedigger
  program.

  Attributes:
    verbose (bool): Verbose output mode
    dry_run (bool): Print actions to the console without performing them

  """

  def __init__(self) -> None:
    """Initialize a Click CLI context"""

    self.verbose = False
    self.dry_run = False
