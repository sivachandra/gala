# GALA

GALA is an adapter package which enables GDB Python API in LLDB. The word
GALA is an acronym for "GDB API over LLDB API". GALA is aimed at making
GDB pretty printers work as LLDB data formatters auto-magically.

## Quick Start Guide

Do the following to start using GALA with LLDB:

  1. Clone the GALA git project:

         git clone https://github.com/sivachandra/gala.git

     For convenience, lets say the path to the cloned git repo
     is path_to_gala.

  2. Add the following lines to your .lldbinit file:

         script import sys
         script import sys.path.append(<path_to_gala>)

  3. [Optional] To enable autoloading of `.debug_gdb_scripts`, add the following
     line (after step 2 from above) to your .lldbinit file:

         command script import autoload

## Wiki

For more information about GALA, visit the project wiki at
https://github.com/sivachandra/gala/wiki.
