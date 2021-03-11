#! /bin/sh

LIB=$1

for ver in `cat $LIB.txt`
do
    image_name="${LIB}_api_extract-$ver"
    echo $image_name
    docker run --add-host=docker.host:172.17.0.1 --rm $image_name
done
