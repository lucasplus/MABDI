
import sys
import os

# needed to create a symlink on either a unix or windows
# (windows is the more difficult case)
# http://stackoverflow.com/a/15043806/4068274
def symlink(source, link_name):
    # import os
    source = os.path.normpath( source )
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()

"""
Assuming a directory structure of 
mabdi/
scripts/
util/
  CreateMabdiSymLinks.py (this file)
"""

# When run from visual studio the current working directory is the one that 
# contains mabdi. Check to see if that is true and if not exit
if not os.path.isdir('mabdi'):
    # maybe I am being run from the "util" folder
    if os.path.isdir('../mabdi'):
        os.chdir('..')
    else:
        sys.exit('I do not know where I am')

# make symbolic links
# remember if you add a symbolic link you have to also
# add it to the .gitignore file
os.chdir('scripts')
symlink('../mabdi','mabdi')
os.chdir('..')