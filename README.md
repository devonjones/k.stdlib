Overview
========
k.stdlib is a set of extensions to the python stdlib
that we've developed in-house, or have gleaned from the
internet.

k.stdlib must not have any dependencies beyond
the python stdlib.

Each extension should live in its own file, under a directory
named after the module it is extending. For example the
defaultnamedtuple method lives in
k/stdlib/collections/defaultnamedtuple.py

Testing
=======
./install_test_dependencies.sh
./mgmt/virtualenv.sh
./mgmt/test.sh
./setup.py sdist
./setup.py test


