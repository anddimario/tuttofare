#!/bin/bash

if [ -z "$SSH_AUTH_SOCK" ] ; then
  eval `ssh-agent -s`
  ssh-add relive
fi

pipenv run python relive.py
