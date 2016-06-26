#!/usr/bin/env bash

nosetests \
    --with-coverage\
    --cover-package=commandargparse \
    --cover-erase \
    --cover-branches
