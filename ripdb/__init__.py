"""
Remote IPython Debugger (ipdb wrapper).
"""

__author__ = "Lev E. Givon"
__version__ = "0.1.3"

import multiprocessing
import os
import pty
import socket
import sys
import threading
import traceback

import IPython.core.debugger as pdb
from IPython.utils import io
import six

try:
    get_ipython
except NameError:
    import IPython.terminal.embed as embed
    InteractiveShellEmbed = embed.InteractiveShellEmbed
    ipshell = InteractiveShellEmbed()
    def_colors = ipshell.colors
else:
    try:
        def_colors = get_ipython.im_self.colors
    except AttributeError:
        def_colors = get_ipython.__self__.colors


class Rpdb(pdb.Pdb):

    def __init__(self, addr="127.0.0.1", port=4444):
        """Initialize the socket and initialize pdb."""

        # Backup stdin and stdout before replacing them by the socket handle
        self.old_stdout = sys.stdout
        self.old_stdin = sys.stdin
        self.port = port

        # Open a 'reusable' socket to let the webapp reload on the same port
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.skt.bind((addr, port))
        self.skt.listen(1)

        # Writes to stdout are forbidden in mod_wsgi environments
        try:
            sys.stderr.write("pdb is running on %s:%d\n"
                             % self.skt.getsockname())
        except IOError:
            pass

        if sys.excepthook != pdb.BdbQuit_excepthook:
            pdb.BdbQuit_excepthook.excepthook_ori = sys.excepthook
            sys.excepthook = pdb.BdbQuit_excepthook

        (clientsocket, address) = self.skt.accept()
        if six.PY3:
            handle = connect_to_pty(clientsocket.makefile('rw', None))
        else:
            handle = connect_to_pty(clientsocket.makefile('r+', 0))           
        io.stdout = sys.stdout = sys.stdin = handle
        pdb.Pdb.__init__(self, def_colors)
        OCCUPIED.claim(port, sys.stdout)

    def shutdown(self):
        """Revert stdin and stdout, close the socket."""
        sys.stdout = self.old_stdout
        sys.stdin = self.old_stdin
        OCCUPIED.unclaim(self.port)
        sys.excepthook = pdb.BdbQuit_excepthook.excepthook_ori
        self.skt.close()

    def do_continue(self, arg):
        """Clean-up and do underlying continue."""
        try:
            return pdb.Pdb.do_continue(self, arg)
        finally:
            self.shutdown()

    do_c = do_cont = do_continue

    def do_quit(self, arg):
        """Clean-up and do underlying quit."""
        try:
            return pdb.Pdb.do_quit(self, arg)
        finally:
            self.shutdown()

    do_q = do_exit = do_quit

    def do_EOF(self, arg):
        """Clean-up and do underlying EOF."""
        try:
            return pdb.Pdb.do_EOF(self, arg)
        finally:
            self.shutdown()


def copy_worker(file_from, file_to):
    while True:
        c = file_from.read(1)
        if not c:
            break
        file_to.write(c)
        if six.PY3:
            file_to.flush()

def connect_to_pty(sock):
    def _multiprocessing_context():
        try:
            return multiprocessing.get_context('fork')
        except (AttributeError, ValueError):
            return multiprocessing

    ptym_fd, ptys_fd = pty.openpty()
    if six.PY3:
        import io
        _ptym = os.fdopen(ptym_fd, 'r+b', 0)
        ptym = io.TextIOWrapper(_ptym, write_through=True)
        _ptys = os.fdopen(ptys_fd, 'r+b', 0)
        ptys = io.TextIOWrapper(_ptys, write_through=True)
    else:
        ptym = os.fdopen(ptym_fd, 'r+', 0)
        ptys = os.fdopen(ptys_fd, 'r+', 0)

    # Setup two processes for copying between socket and master pty.
    sock_to_ptym = _multiprocessing_context().Process(
        target=copy_worker,
        args=(sock, ptym)
    )
    sock_to_ptym.daemon = True
    sock_to_ptym.start()
    ptym_to_sock = _multiprocessing_context().Process(
        target=copy_worker,
        args=(ptym, sock)
    )
    ptym_to_sock.daemon = True
    ptym_to_sock.start()
    return ptys


def set_trace(addr="127.0.0.1", port=4444):
    """Wrapper function to keep the same import x; x.set_trace() interface.

    We catch all the possible exceptions from pdb and cleanup.

    """
    try:
        debugger = Rpdb(addr=addr, port=port)
    except socket.error:
        if OCCUPIED.is_claimed(port, sys.stdout):
            # rpdb is already on this port - good enough, let it go on:
            sys.stdout.write("(Recurrent rpdb invocation ignored)\n")
            return
        else:
            # Port occupied by something else.
            raise
    try:
        debugger.set_trace(sys._getframe().f_back)
    except Exception:
        traceback.print_exc()


class OccupiedPorts(object):
    """Maintain rpdb port versus stdin/out file handles.

    Provides the means to determine whether or not a collision binding to a
    particular port is with an already operating rpdb session.

    Determination is according to whether a file handle is equal to what is
    registered against the specified port.
    """

    def __init__(self):
        self.lock = threading.RLock()
        self.claims = {}

    def claim(self, port, handle):
        self.lock.acquire(True)
        self.claims[port] = id(handle)
        self.lock.release()

    def is_claimed(self, port, handle):
        self.lock.acquire(True)
        got = (self.claims.get(port) == id(handle))
        self.lock.release()
        return got

    def unclaim(self, port):
        self.lock.acquire(True)
        del self.claims[port]
        self.lock.release()

# {port: sys.stdout} pairs to track recursive rpdb invocation on same port.
# This scheme doesn't interfere with recursive invocations on separate ports -
# useful, eg, for concurrently debugging separate threads.
OCCUPIED = OccupiedPorts()
