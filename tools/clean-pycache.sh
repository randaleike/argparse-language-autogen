#!/bin/bash

# Cleanup python cache directories
find . -name "__pycache__" -exec rm -rf "{}" \;


# Check if we need to clean the env directory
if [ -d "./env" ]
then
    read -p "Clean env: (y/n)?" yn
    case $yn in
        [Yy]*) rm -rf ./env;;
        *) ;;
    esac
fi

# Check if we need to clean the test directory
if [ -d "./test" ]
then
    read -p "Clean test: (y/n)?" yn
    case $yn in
        [Yy]*) rm -rf ./test;;
        *) ;;
    esac
fi
