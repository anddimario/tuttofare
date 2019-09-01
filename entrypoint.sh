#!/bin/bash

if [ -z "$SSH_AUTH_SOCK" ] ; then
  eval `ssh-agent -s`
  ssh-add tuttofare
fi

pipenv run python tuttofare.py
