#!/bin/bash
# From walk through on CTF Quals 2008
#
# Script assumes the dir is in a mounted image of the file
# e.g. the file is a disk  image, and dir is in that image 

if [ $# != 2 ]
then
  echo "strings_outside_dir.sh <disk_image_file> <dir_in_the_image>"
  exit
fi

dir=$2
file=$1

strings -a $file | while read line
do
  grep -q "$line" $dir/* || echo "$line"
done
