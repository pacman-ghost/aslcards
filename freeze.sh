#!/bin/bash

# initialize
BASE_DIR=$(readlink -f "`dirname "$0"`")
RELEASE_FILENAME="/tmp/asl_cards.tar.gz"

# freeze the application
cd "$BASE_DIR"
rm -rf build
python _freeze.py build
if [ $? -ne 0 ] ; then
    echo "ERROR: Freeze failed."
    exit $?
fi

# create the release
cd build/exe.linux-x86_64-3.6
tar cfz "$RELEASE_FILENAME" .
echo
echo "Created release:"
ls -lh "$RELEASE_FILENAME" | sed -e "s/^/  /"

# clean up
rm -rf "$BASE_DIR/build"
