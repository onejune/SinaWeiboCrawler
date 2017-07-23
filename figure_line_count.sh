#!/bin/bash
all_lines=0
function calculate_line(){
    for element in `ls $1`
    do
        dir_or_file=$1'/'$element
        if [ -d $dir_or_file ]
        then
            calculate_line $dir_or_file
        else
            lines=`wc -l $dir_or_file | awk '{print $1}'`
            let all_lines=$all_lines+$lines
        fi
    done
}

root_dir=$1
calculate_line $root_dir
echo $all_lines
