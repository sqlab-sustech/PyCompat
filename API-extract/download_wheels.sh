#! /bin/sh

pip3.5 download pymongo -d ./wheels/common/
pip3.5 download parso -d ./wheels/common/

LIB=$1
echo $LIB
for ver in `cat $LIB.txt`
do
    mkdir -p ./wheels/$LIB/$ver/
    pip3.5 download $LIB==$ver -d ./wheels/$LIB/$ver/
done
