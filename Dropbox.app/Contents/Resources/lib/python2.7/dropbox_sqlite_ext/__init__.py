#
# Copyright (c) Dropbox, Inc.
#

from __future__ import absolute_import, print_function

import contextlib
import os
import pkg_resources
import re
import shutil
import traceback
import sys
import tempfile
import threading
import uuid

try:
    from dropbox.trace import TRACE, report_bad_assumption, unhandled_exc_handler
except ImportError:

    def TRACE(s, *n):
        if n:
            s %= n
        print(s, file=sys.stderr)

    def report_bad_assumption(s, *n, **kwargs):
        if n:
            s %= n
        print(s, file=sys.stderr)

    def unhandled_exc_handler():
        traceback.print_exc(file=sys.stderr)

class BrokenTempDirError(Exception):
    pass

class DropboxSqliteExtension(object):

    package_name = __name__     # 'dropbox_sqlite_ext', for accessing pkg_resources
    dll_name = 'dropbox_sqlite_ext'

    def __init__(self):
        self._lock = threading.Lock()
        self._extracted_lockfile = None
        self._extracted_filename = None

    def __sqlite_pathencode(self, path):
        # The argument to load_extension is a bytestring that will be passed to
        # `pVfs->xDlOpen()` after appending '.dylib' or '.so'.
        if isinstance(path, bytes):
            return path
        if os.name == 'nt':
            # `winDlOpen` expects a UTF-8 path (!).  See sqlite3.c
            return path.encode('utf-8')
        else:
            return path.encode(sys.filesystemencoding())

    def load_extension(self, conn):
        """Load the SQLite extension on the specified SQLite connection.

        You must have already enabled extension loading on the connection
        with `enable_load_extension()`.
        """
        import sqlite3
        # SQLite 3.7.17 and later versions add the dll suffix themselves.
        conn.load_extension(self.__sqlite_pathencode(self.dll_filename_without_suffix))

    @property
    def dll_suffix(self):
        """Return the dll suffix for this platform.

        Example: '.dll'
        """
        if sys.platform == "win32":
            return ".dll"
        elif sys.platform == "darwin":
            return ".dylib"
        else:
            return ".so"

    @property
    def dll_basename(self):
        """The basename of the SQLite extension dll.

        Example: 'dropbox_sqlite_ext.dll'
        """
        return "%s%s" % (self.dll_name, self.dll_suffix)

    @property
    def dll_filename(self):
        """The full path to the SQLite extension dll."""
        try:
            return pkg_resources.resource_filename(self.package_name, self.dll_basename)
        except NotImplementedError:
            # py2exe bundles the DLL inside the executable, but sqlite needs to
            # have a real filename, so we extract it into a temporary directory.
            with self._lock:
                if self._extracted_filename is not None:
                    return self._extracted_filename

                if sys.platform.startswith("win"):
                    self._win32_extract()
                    return self._extracted_filename
                else:
                    raise

    @property
    def dll_filename_without_suffix(self):
        """
        Return the full path to the SQLite extension, without .dll/.dylib/.so

        Newer versions of SQLite will append the file extension themselves, so we
        strip it here.
        """
        return self.dll_filename.rsplit('.', 1)[0]

    def _win32_extract(self):
        # We need to extract the .dll to a temporary file so that
        # sqlite3_load_extension can find it, but we don't want temporary files
        # to accumulate over time.  Windows temp directories aren't cleaned up
        # regularly (and there's apparently no way to use
        # FILE_FLAG_DELETE_ON_CLOSE with LoadLibrary that will actually work)
        # so we create a unique, constant prefix for our dll, and attempt to
        # clean up older dlls matching the same prefix, unless another process
        # is using them.
        #
        # To determine whether another process is using the DLLs, we hold open
        # a lock file.
        #
        # Example DLL & lock name:
        #   C:\Users\dlitz\AppData\Local\Temp\dropbox_sqlite_ext.{5f3e3153-5bce-5766-8f84-3e3e7ecf0d81}.tmpfc6wu23.dll
        #   C:\Users\dlitz\AppData\Local\Temp\dropbox_sqlite_ext.{5f3e3153-5bce-5766-8f84-3e3e7ecf0d81}.tmpfc6wu23.lck

        TRACE("%s: Need to extract %s to temporary directory", self.dll_name, self.dll_basename)

        import msvcrt
        import win32api
        import win32file as wf
        import winerror

        # Compute the dll prefix
        ns_uuid = uuid.UUID('125626a0-9d3a-4aeb-b2ed-5770cb0665cc')
        dll_uuid = uuid.uuid5(ns_uuid, "%s.%s" % (self.package_name, self.dll_name))
        tmp_prefix = "%s.{%s}.tmp" % (self.dll_name, dll_uuid)
        lck_suffix = ".lck"
        dll_regex = re.compile("^(%s.*)%s$" % (re.escape(tmp_prefix), re.escape(self.dll_suffix)), re.I | re.S)
        lck_regex = re.compile("^(%s.*)%s$" % (re.escape(tmp_prefix), re.escape(lck_suffix)), re.I | re.S)

        def dll_to_lck(dllfilename):
            dirname = os.path.dirname(dllfilename)
            basename = os.path.basename(dllfilename)
            m = dll_regex.search(basename)
            if not m:
                raise ValueError("no match: %r" % (basename,))  # should never happen
            new_basename = "%s%s" % (m.group(1), lck_suffix)
            return os.path.join(dirname, new_basename)

        def lck_to_dll(lckfilename):
            dirname = os.path.dirname(lckfilename)
            basename = os.path.basename(lckfilename)
            m = lck_regex.search(basename)
            if not m:
                raise ValueError("no match: %r" % (basename,))  # should never happen
            new_basename = "%s%s" % (m.group(1), self.dll_suffix)
            return os.path.join(dirname, new_basename)

        def can_read_and_execute(filename):
            try:
                h2 = wf.CreateFileW(filename, wf.GENERIC_READ | wf.GENERIC_EXECUTE, 0, None, wf.OPEN_EXISTING, 0, None)
                h2.Close()
                return True
            except wf.error as e:
                if e.winerror == winerror.ERROR_ACCESS_DENIED:
                    return False
                else:
                    raise

        # Get the temporary directory
        temp_dir = tempfile.gettempdir()
        TRACE("%s: Temporary directory is %r", self.dll_name, temp_dir)

        # Try to delete old files that match the dll prefix
        try:
            for basename in os.listdir(temp_dir):
                # If this file matches prefix*.dll
                m = dll_regex.search(basename)
                if m:
                    filename = os.path.join(temp_dir, basename)
                    lockfilename = dll_to_lck(filename)

                    # Try to delete the lockfile first
                    try:
                        os.unlink(lockfilename)
                    except WindowsError as e:
                        if e.winerror == winerror.ERROR_FILE_NOT_FOUND:
                            TRACE("!! %s: Lock file already gone: %r", self.dll_name, lockfilename)
                            pass
                        elif e.winerror == winerror.ERROR_SHARING_VIOLATION:
                            # File still in use.  Ignore it.
                            TRACE("%s: Lock file still in use: %r", self.dll_name, lockfilename)
                            continue
                        else:
                            unhandled_exc_handler()
                            TRACE("!! %s: Unhandled exception while trying to delete lock file %r",
                                  self.dll_name, lockfilename)
                            continue
                    else:
                        TRACE("%s: Lock file deleted: %r", self.dll_name, lockfilename)

                    # OK, now delete the dll.
                    TRACE("%s: Deleting %r ...", self.dll_name, filename)
                    try:
                        os.unlink(filename)
                    except WindowsError as e:
                        if e.winerror == winerror.ERROR_FILE_NOT_FOUND:
                            TRACE("!! %s: DLL already gone: %r", self.dll_name, filename)
                            pass
                        else:
                            unhandled_exc_handler()
                            continue
                    else:
                        TRACE("%s: Deleted: %r", self.dll_name, filename)
        except:
            unhandled_exc_handler()

        # Safely create a .dll & .lck pair
        # outputs: outfile, outfilename, lockfile, lockfilename
        TRACE("%s: Creating .dll & .lck pair ...", self.dll_name)
        for retry in range(10):
            # Make a new .lck file.
            lockfile = tempfile.NamedTemporaryFile(prefix=tmp_prefix,
                                                   suffix=lck_suffix,
                                                   delete=False)
            lockfilename = lockfile.name
            TRACE("%s: Opened lock file: %r", self.dll_name, lockfilename)
            dllfilename = lck_to_dll(lockfilename)

            # Safely create a .dll file with the same prefix.
            h = wf.CreateFileW(dllfilename, wf.GENERIC_WRITE, 0, None, wf.CREATE_NEW, wf.FILE_ATTRIBUTE_NORMAL, None)
            dllfile = os.fdopen(msvcrt.open_osfhandle(h.Detach(), 0), "wb")
            TRACE("%s: Opened dll file: %r", self.dll_name, dllfilename)

            break
        else:
            raise AssertionError("Too many retries when attempting to create temporary file")

        # Make sure the lockfile can't be deleted
        TRACE("%s: Sanity check...", self.dll_name)
        try:
            os.unlink(lockfilename)
        except WindowsError as e:
            if e.winerror != winerror.ERROR_SHARING_VIOLATION:
                unhandled_exc_handler()
        else:
            report_bad_assumption("%s: lockfile successfully deleted while still in use.  This will race!  %r",
                                  self.dll_name, lockfilename)

        if not os.path.exists(lockfilename):
            report_bad_assumption("%s: lockfile successfully deleted while still in use.  This will race!  %r",
                                  self.dll_name, lockfilename)

        # Need these assertions, or pkg_resources.resource_stream will break on
        # Windows when installing from a non-ascii directory.
        assert isinstance(self.package_name, str)
        assert isinstance(self.dll_basename, str)

        # Write the dll contents
        TRACE("%s: Writing dll contents: %r", self.dll_name, dllfilename)
        with contextlib.closing(pkg_resources.resource_stream(self.package_name, self.dll_basename)) as infile:
            shutil.copyfileobj(infile, dllfile)

        # Close the .dll file (otherwise, sqlite won't be able to load it)
        dllfile.close()

        # Test that we can load the dll
        TRACE("%s: Testing LoadLibrary: %r", self.dll_name, dllfilename)
        try:
            dllhandle = win32api.LoadLibrary(dllfilename)
        except win32api.error as e:
            TRACE("!! %s: LoadLibrary(%r) failed (error %r, %r)", self.dll_name, dllfilename, e.winerror, e.strerror)
            if e.winerror == winerror.ERROR_ACCESS_DENIED and not can_read_and_execute(dllfilename):
                # Apparently, some software screws with the permissions of the
                # temporary directory.  Other stuff on the user's machine will
                # be broken, but we at least want to show a reasonable error
                # message.
                #
                # "Acrobat replaces NTFS permissions of Temp folder"
                #   http://forums.adobe.com/message/5033519
                # "BUG! Acrobat XI screws up permissions of Temp folder causing problems with other programs/installers"
                #   http://forums.adobe.com/thread/1159899
                raise BrokenTempDirError(
                    "Broken temporary directory (missing execute permission): %r" % (os.path.dirname(dllfilename),))

            # Failed for some other reason.  Just raise the original exception.
            raise
        else:
            TRACE("%s: LoadLibrary succeeded.  Freeing: %r", self.dll_name, dllfilename)
            win32api.FreeLibrary(dllhandle)
            del dllhandle

        # Keep a reference to the lockfile
        self._extracted_lockfile = lockfile

        # Save the path to the dll
        self._extracted_filename = dllfilename

        TRACE("%s: Done extracting %s to %r", self.dll_name, self.dll_basename, self._extracted_filename)

_loader = DropboxSqliteExtension()
load_extension = _loader.load_extension

def get_dll_basename():
    """Return the basename of the SQLite extension dll.

    Example: 'dropbox_sqlite_ext.dll'
    """
    return _loader.dll_basename

def get_dll_filename():
    """Return the full path to the SQLite extension dll."""
    return _loader.dll_filename
