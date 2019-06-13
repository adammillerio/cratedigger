# cratedigger

cratedigger is a tool for syncing a music library with Serato crates. This allows for those who do not use iTunes to more convienently manage their Serato library.

This project is a Python update of the abandoned [serato-itch-sync](https://code.google.com/archive/p/serato-itch-sync/) tool with some additional features and enhancements.

cratdigger is compatible with both MacOS and Windows.

# Installation

To install cratedigger, you will need Python 3 and Pip.

On Windows, it is recommended that you use the [ActivePython](https://www.activestate.com/products/activepython/) distribution of Python 3, as it comes with Pip.

On MacOS, [Homebrew](https://brew.sh/) is recommended.

Once Python3 and Pip are installed, run the following command to install cratedigger:

`pip3 install cratedigger`

# Usage

cratedigger is a command line tool, so it must be run from either cmd/PowerShell on Windows or Terminal on MacOS.

There are two global command line flags:

* `--verbose` - Enable verbose output
* `--dry-run` - Do not actually write any crate files

## Sync

The sync command allows for mirroring a directory structure within a Serato library. This command will traverse a given music directory and add all compatible music files to their respective crates, and then write them to the Serato library on the volume.

This command effectively mirrors the functionality of serato-itch-sync, with some important distinctions:

* It will automatically detect the proper directory to store subcrates, unless overridden with `--serato-dir`
* It will prefix all crates with Media/\<Volume Name> in order to prevent overlapping crates when syncing multiple libraries
* It will not clear the Serato Subcrates directory at any point, leaving existing crates that do not use the Media/\<Volume Name> prefix untouched

Example:

On the C drive there is a music library with the following structure:

```
Library/Music
└── Library/Music/V2
    └── Library/Music/V2/8mm
        ├── Library/Music/V2/8mm/8mm - Opener EP
        └── Library/Music/V2/8mm/8mm - Songs to Love and Die By
```
To sync this library, run the following command:

```
cratedigger sync --library-dir=C:\Library
```

This will load all media in this directory and write the following crates in the `C:\Users\<Username>\Music\_Serato_\Subcrates` directory:

```
C.crate
Media%%C%%Library.crate
Media%%C%%Library%%Music.crate
Media%%C%%Library%%Music%%V2.crate
Media%%C%%Library%%Music%%V2%%8mm.crate
Media%%C%%Library%%Music%%V2%%8mm%%8mm - Songs to Love and Die By.crate
Media%%C%%Library%%Music%%V2%%8mm%%8mm - Opener EP.crate
```

All crates loaded from a media library are prefixed with Media/\<Volume Name> to prevent overlapping crates when syncing several directories.

These will show in Serato as follows:

```
Media/C
└── Media/C/Library/Music/V2
    └── Media/C/Library/Music
        └── Media/C/Library/Music/V2
            └── Media/C/Library/Music/V2/8mm
                ├── Library/Music/V2/8mm/8mm - Opener EP
                └── Library/Music/V2/8mm/8mm - Songs to Love and Die By
```
# Development

## Building

To install cratedigger, clone this repository and run the following command:

```
pip3 install .
```

Optionally, it can be installed in development mode, which allows for iteration on the current repository without reinstalling:

```
pip3 install -e .
```

## Testing

### mypy

This repository has MyPy type hints for type enforcement.

To use these, first install mypy:

```
pip3 install mypy
```

Then, run the following command from the root of the repository:

```
mypy cratedigger
```
