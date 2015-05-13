.. -*- rst -*-

Remotely Accessible IPython-Enabled Debugger
============================================

Package Description
-------------------
ripdb is a wrapper around the IPython debugger that enables one to connect to
and control the debugger remotely via a socket handler. It combines
the functionality of `ipdb <https://github.com/gotcha/ipdb>`_ and `rpdb
<https://github.com/tamentis/rpdb>`_ in a single package.

.. image:: https://img.shields.io/pypi/v/ripdb.svg
    :target: https://pypi.python.org/pypi/ripdb
    :alt: Latest Version

Usage
-----
After installation, include the following in your code: ::

  import ripdb
  ripdb.set_trace()

This will start the debugger on port 4444 by default; to use a different port
instantiate the debugger as follows: ::

  import ripdb
  debugger = ripdb.Rpdb(port=12345)
  debugger.set_trace()

Connect to the debugger using a telnet client.

Development
-----------
The latest release of the package may be obtained from
`GitHub <tthps://github.com/lebedov/ripdb>`_.

Authors
-------
See the included AUTHORS.rst file for more information.

License
-------
This software is licensed under the 
`GNU General Public License, version 2 <https://www.gnu.org/licenses/gpl-2.0.html>`_.
See the included LICENSE.rst file for more information.
