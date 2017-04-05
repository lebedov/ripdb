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
  ripdb.set_trace(port=12345)

Connect to the debugger using telnet, netcat, or socat. If you want to enable 
line completion and editing, you need to disable several terminal features 
before connecting: ::

  SAVED_STTY=`stty -g`; stty -icanon -opost -echo -echoe -echok -echoctl 
  -echoke; nc 127.0.0.1 4444; stty $SAVED_STTY

Development
-----------
The latest release of the package may be obtained from
`GitHub <tthps://github.com/lebedov/ripdb>`_.

Authors
-------
See the included `AUTHORS
<https://github.com/lebedov/ripdb/blob/master/AUTHORS.rst>`_ file for more
information.

License
-------
This software is licensed under the `BSD License
<http://www.opensource.org/licenses/bsd-license.php>`_.  See the included
`LICENSE <https://github.com/lebedov/ripdb/blob/master/LICENSE.rst>`_ file for
more information.
