import lit.formats
import os
from pathlib import Path

config.name = "GALA"
config.test_format = lit.formats.ShTest()
config.suffixes = [".test"]

# Add the root GALA directory to PYTHONPATH so we can `import gdb`.
test_directory = Path(__file__).resolve().parent
gala_directory = test_directory.parent.parent
config.environment['PYTHONPATH'] = os.pathsep.join([
    str(gala_directory), str(gala_directory / 'gdb_modules')
])

# Substitutions for common tools. Assume them to be in the PATH for now.
config.substitutions.append( ('%clangxx', 'clang++') )
config.substitutions.append( ('%clang', 'clang') )
config.substitutions.append( ('%lldb', 'lldb -S lldbinit-gala') )
