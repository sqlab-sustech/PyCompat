#! /bin/sh

LIB=$1

for ver in `cat $LIB.txt`
do
    mkdir -p ./$LIB/image/$ver/whl
    cp ./wheels/$LIB/$ver/* ./$LIB/image/$ver/whl/
    cp ./wheels/common/* ./$LIB/image/$ver/whl/
done
