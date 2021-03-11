#! /bin/sh

LIB=$1

for ver in `cat $LIB.txt`
do
    image_name="${LIB}_api_extract-$ver"
    if [ "$(docker image ls | grep $image_name)" ]
    then
        docker image rm $image_name
    else
        echo "$ver" not exist
    fi
done
