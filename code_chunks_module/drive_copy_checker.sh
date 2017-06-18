#!/bin/bash
# 
# Automated file copy and MD5 checker script
#
#  Functionalities:
#  1) Automatically format a USB FOB and create a Fat32 partition
#  2) Mount the USB FOB
#  3) Copy files from a Source to a Destination directory on the FOB
#  4) Perform an MD5 check on the files in a given list based on a relative directory
#  5) Create an MD5 list for a set of given files
#
#  This script will need to be run as root.  
#  CAUTION: THIS SCRIPT CAN AND WILL DESTROY DATA IF NOT CAREFULLY WIELDED, BE WARNED!!
#
# 
# Adam Pridgen 2008
#
# Licensed under the MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software 
# without restriction, including without limitation the rights to use, copy, modify, merge, 
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons 
# to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


device=""
mount_dir=""
comp_dir=""
md5_list=""
src_dir=""
dst_dir=""

execution_method=""
create_md5list=0
md5_dirlist=''
format=""
formatSize=""


print_usage()
{
echo
echo
echo "The following are the intended calling methods for this script:"
echo "fschecker.sh -s <src_dir> -d <dst_dir> -m <device_to_Mount> -D <dir_to_mount_to>"
echo "fschecker.sh -s <src_dir> -d <dst_dir> -m <device_to_Mount> -D <dir_to_mount_to> -M <md5_file_list>"
echo "fschecker.sh -c <dir_to_check_md5s> -m <md5_file_list>"
echo "fschecker.sh -C <file_to_hold_md5> <dir_or_file_to_create_md5s_for> ..."
echo "     -s is the base of source directory to copy files from
    -M is the mount point for the device and files are copied too
    -d is the destination directory (not required, mount_dir is used as base directory in that case )
    -D is the the device to mount 
    -c is the base directory to compare files against with MD5
    -C specify creating an MD5 file list from specified directories
    -m is the list of files and MD5 sums, starts from base of src directory or comparison directory (required if -c is specified)
    -F format followed by the size of the drive in MB (e.g. 2042MB) 
    "

echo "Examples"
echo
echo "  Create a list of MD5s for the specified location (relative dirs are used)"
echo "    ./fschecker.sh -C md5list.txt data/"
echo
echo "  Copy files from src to dst directory, and then perform an MD5 Check."
echo "    ./fschecker.sh -s data/ -d compare/ -m md5list.txt"
echo
echo "  Mount, Copy, Check MD5s, and Umount drive."
echo "  The later will use the root of the drive as the dst directory."
echo "    ./fschecker.sh -D /dev/sdd -M usb/ -s data/ -d blah/ -m md5list.txt"
echo "    ./fschecker.sh -D /dev/sdd -M usb/ -s data/ -m md5list.txt"
echo
echo "  Format, Create a 257MB Fat32 Partition, Mount, Copy, Check MD5s, and Umount drive."
echo "  The later will use the root of the drive as the dst directory."
echo "    ./fschecker.sh -F 257MB -D /dev/sdd -M usb/ -s data/ -d blah/ -m md5list.txt"
echo "    ./fschecker.sh -F 257MB -D /dev/sdd -M usb/ -s data/ -m md5list.txt"
echo
echo "  Format, Create a 257MB Fat32 Partition, Mount, Copy, and Umount drive."
echo "  The later will use the root of the drive as the dst directory."
echo "    ./fschecker.sh -F 257MB -D /dev/sdd -M usb/ -s data/ -d blah/"
echo "    ./fschecker.sh -F 257MB -D /dev/sdd -M usb/ -s data/"
echo
echo "  Mount Drive, Check MD5s, and Umount drive."
echo "  The later will use the root of the drive as the dst directory."
echo "    ./fschecker.sh -D /dev/sdd -M usb/ -m md5list.txt" 
echo
echo "  Check MD5s on a given directory."
echo "    ./fschecker.sh -m md5list.txt -c data/" 


}


getopt_pair()
{
    until [ -z "$1" ]
    do
      if [ ${1:0:1} = '-' ]
      then
          #if [ ${2:0:1} = '-' ]
	  #then
	  #	print_usage
	  #      exit
	  #fi
	  set_param $1 $2 
	  if [ $1 = '-C' ]
	  then
	    return
	  fi
      fi
      shift 2
    done
}
set_param()
{
  case "$1" in
    "-s") echo "Source Directory is $2";
    	 src_dir=$2;;
    "-D") echo "Device to mount is $2";
    	 device=$2;;
    "-m") echo "MD5 file list is $2";
    	 md5_list=$2;;
    "-M") echo "Directory to mount device to is $2";
    	 mount_dir=$2;;
    "-d") echo "Destination to copy files is $2";
    	 dst_dir=$2;;
    "-c") echo "Directory to check MD5s is $2";
    	 comp_dir=$2;;
    "-F") echo "Will format the drive with a $2 fat32 partition";
         format="true";
         formatSize=$2;;
    "-C") echo "Creating MD5 list in file $2";
         md5_list=$2; 
         create_md5list=1;;
  esac
}

set_run_criteria()
{
# A helper function to decide what operation to conduct, as can be seen below
#
  echo "Setting execution criteria."
  if [[ -n $device &&  -n $mount_dir && -n $src_dir && -n $md5_list ]]
  then 
  	return 0 #"CopytoDriveMD5"
  elif [[ -n $device &&  -n $mount_dir && -n $src_dir ]]
  then 
  	return 1 #"CopytoDrive"
  elif [[ -n $src_dir &&  -n $dst_dir && -n $md5_list ]]
  then 
  	return 4 #"CopyFilesCompMD5"
  elif [[ -n $comp_dir &&  -n $device &&  -n $mount_dir && -n $md5_list ]]
  then 
  	return 2 #"CompFilesOnDrive"
  elif [[ -n $comp_dir &&  -n $md5_list ]]
  then 
  	return 3 #"CompFiles"
  else
     echo "Bad parameters were passed to the program!"
     echo "device: $device"
     echo "mount_dir: $mount_dir"
     echo "src_dir: $src_dir"
     echo "md5_list: $md5_list"
     echo "comp_dir: $comp_dir"
     print_usage
     exit
  fi
}
format()
{
# format is just a wrapper to parted.  it bruteforce deletes the the 4 primary partitions, and
# then adds a single fat32 partion of the provided size.
#
# $1 is the device to format
# $2 is the size in MB (e.g. 2042MB Note the explicit MB at the end!)

  parted -s $1 rm 1
  parted -s $1 rm 2 
  parted -s $1 rm 3
  parted -s $1 rm 4
  echo "Creating the Fat32 Partition on $1 with a size of $2."
  parted -s $1 mkpartfs primary fat32 0 $2
  sleep 2
}

mount_drive()
{
# mount the drive to have the file copied to it or have the 
# MD5 sums for files checked
#
# $1 is the device to mount
#
# $2 is the directory mount point
#
  if [ $# != 2 ] 
  then
    echo "Wrong number of command args for mount command: $#";
    return  1;
  fi
  echo "mounting $1 to $2"

  mount $1'1' $2
  if [ $? != 0 ]
  then 
    echo "Note: This is a privileged operation and failed because the current user has inadequate privileges!"
    exit;
  fi
}

copy_files()
{
# Copy files from a source location to a variable destination location
# The destination is derived from the directory where the drive is mounted
# along with a destination directory in the drive.  If the destination directory
# is not specified, the mount directory is consider the directory to data to.
#
# $1 is the src_dir value, or Source directory
#
# $2 is the mount_dir+'/'+dst_dir or the destination directory 
  
  
  basename=${2##*/}
  
  if [ -e ${2%%$basename} ]
  then 
    continue 
  else
    echo "Directory does not exist, creating the base directory."  
    mkdir -p ${2%%$basename}
  fi
  echo "Copying files $1 to $2."
  cp -rf $1 $2
}

compare_md5list()
{
# compare the MD5 hash for a filename in a given list to
# another file, using a base directory to locate the file
#
# $1 is the file or base directory that will be used to 
# locate and create an MD5 sum
#
# $2 is the md5list file which is a list of results from
# md5 on a set of files
#
# The function will report any files that fail the check in
# $PWD/ErrorLog.txt.  If the files is not found, a failure is 
# recorded

  error="ErrorLog.txt"
  echo "Starting the MD5 sum check"

  if [ -e $1 ]
  then
    cat $1 |
    while read md5_sum filename 
    do
      
      ifilename=$2'/'$filename
      imd5sum=""
      if [ -e $ifilename ] 
      then 
        imd5sum=$(md5 $ifilename | awk '{print $1}')
      else	
	echo "Could not find $ifilename represented by $filename in the list!"
	echo "Could not find $ifilename represented by $filename in the list!" >> $error
        continue
      fi
      
      if [ $imd5sum != $md5_sum ]
      then 
	echo "MD5 sums for $ifilename and $filename do not match!"
	echo "MD5 sums for $ifilename and $filename do not match!" >> $error
	continue
      fi
      echo "MD5s match $ifilename == $filename"
    done
  else
    echo "Could not find the MD5 sum list: $1"
  fi
  echo "Completed the MD5 sum check"
}

create_md5()
{
# create an MD5 hash of a given file and append
# the result to the file name specified by $md5_list
# Uses md5 binary on a unix system
#
# $1 is the file or directory to MD5 sum
#
# $2 is the md5_list file name
#
# not a pure recursive function, the logic in the first if 
# block will create an md5 sum if it is a file rather than 
# calling itself again.  this might add a little speed up
#
  if [[ -e $1 && -d $1 ]]
  then 
    for element in $1/*;
    do
      if [[ -e $element && -f $element ]]
      then
        echo "MD5 of $element is taking place"
	md5 $element >> $2
      elif [[ -e $element && -d $element ]]
      then 
        create_md5 $element $2 
      else
        echo "Skipping file because it is not a file or directory: $element"
      fi
    done
  elif [[ -e $1 && -f $1 ]]
  then
    echo "MD5 of $1 is taking place"
    md5 $1 >> $2
  fi
}

start_recursive_md5()
{
# create an MD5 hash of a given file and append
# the result to the file name specified by $md5_list
# Uses md5 binary on a unix system
# Takes in all global command args and shifts them by 2 to get the
# start of the directories.  Calls create_md5sum
  shift 2 

  until [ -z $1 ]
  do
    echo "Starting Recursive MD5 on directory $1"
    if [ -e $1 ]
    then
      create_md5 $1 $md5_list 
    fi
    shift
  done
  echo "Completed recursive MD5 on directories to complete."
}

CopyFilesCompMD5(){
  
  copy_files $src_dir $dst_dir
  compare_md5list $md5_list $dst_dir
}

CompFilesOnDrive()
{
  mount_drive $device $mount_dir
  basedir=$mount_dir'/'$comp_dir
  compare_md5list $md5_list $basedir
}

CompFiles()
{
  basedir=$comp_dir
  compare_md5list $md5_list $basedir
}

CopytoDrive()
{
  
  if [[ $format == 'true' &&  -n $device ]]
  then
    echo "Formatting $device with a $formatSize partition."
    format $device $formatSize 
  fi
  
  mount_drive $device $mount_dir
  dst=''
  if [ -n $dst_dir ]
  then
    dst=$mount_dir'/'$dst_dir'/'
  else
    dst=$mount_dir'/'
  fi
  copy_files $src_dir $dst

}

CopytoDriveMD5()
{
  CopytoDrive
  basedir=$mount_dir'/'$dst_dir
  echo "Checking the MD5 on the files in $basedir using $md5_list"
  compare_md5list $md5_list $basedir

}

# Pass all options to getopt_simple().
getopt_pair $*

# create the MD5 checksum list
if [ $create_md5list -eq 1 ]
then 
  echo "Creating md5 checksum"
  start_recursive_md5 $*
  exit
fi

set_run_criteria
exec_method=$?

echo "exec_method: $exec_method"

case $exec_method in
  0) echo "Copying files to drive then performing the MD5 check."
  		    CopytoDriveMD5;;
  1) echo "Only copying files to drive."
  		    CopytoDrive;;
  2) echo "Performing an MD5 check of the files on the drive."
  		    CompFilesOnDrive;;
  3) echo "Performing an MD5 check of the files on the drive."
  		    CompFiles;;
  4) echo "Copying files to a directory and checking MD5s."
  		    CopyFilesCompMD5;;
  *)  echo "Could not finish the copy or MD5 check.  Missing parameters?";
      echo ""
      print_usage;
      exit;;
esac

if [[ -n $device && -n $mount_dir  ]]
then 
  umount $mount_dir
fi

echo "Finished whatever your bidding was (hopefully I was right :))"

