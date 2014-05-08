Overview
========
kstdlib is a set of extensions to the python stdlib
that we've developed in-house, or have gleaned from the
internet.

kstdlib must not have any dependencies beyond
the python stdlib.

Each extension should live in its own file, under a directory
named after the module it is extending. For example the
defaultnamedtuple method lives in
kstdlib/collections/defaultnamedtuple.py

To deal with issues of upgrading, on my fork, I've renamed this package
to kstdlib.

Code is copyright Knewton Inc 2009-2014, with modifications by Devon Jones
copyright 2014

Testing
=======
./install_test_dependencies.sh
./mgmt/virtualenv.sh
./mgmt/test.sh
./setup.py sdist
./setup.py test


