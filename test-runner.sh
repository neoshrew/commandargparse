#!/usr/bin/env bash

while getopts "23" opt;
do
    case $opt in
        2)
            DO_2=Y
            ;;
        3)
            DO_3=Y
            ;;
    esac
done

if [ -z $DO_2 ] && [ -z $DO_3 ];
then
    DO_2=Y
    DO_3=Y
fi

if [[ $DO_2 == Y ]];
then
    nosetests-2.7 \
        --with-coverage\
        --cover-package=commandargparse \
        --cover-erase \
        --cover-branches
fi

if [[ $DO_3 == Y ]];
then
    nosetests-3.4 \
        --with-coverage\
        --cover-package=commandargparse \
        --cover-erase \
        --cover-branches
fi
