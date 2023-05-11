#!/bin/bash

# Check that two parameters are passed.

if [ $# -ne 2 ] 
  then
    echo "This script requires two arguments: <OPENAI_API_KEY> and"
    echo "<API_SECRET>. The first is available from the OpenAI website and"
    echo "the latter is your own value to be used as an API password."
    exit 1
fi

NAME=breakfree-dk-with-openai-chat

# Create container

echo -e "\n## Create $NAME container\n"

toolbox rm --force $NAME || true
toolbox create --container $NAME

# Install applications

echo -e "\n## Install $NAME tools and applications\n"

RUN="toolbox run --container $NAME"

## List of applications to be installed

APPLICATIONS=( pandoc \ 
               python3-pandas \
               cmake gcc-c++ blas-devel lapack-devel swig )

## Install applications

echo "### Installing applications:"
for app in ${APPLICATIONS[@]}; do
  echo -e "\n--- Installing $app ---\n";
  $RUN sudo dnf install -y $app;
  echo -e "\n--- $app installed ---\n";
done

## Link `podman` to local host binaries
$RUN sudo bash -c 'echo -e "\
export OPENAI_API_KEY=$1 \n\
export API_SECRET=$2 "\
> /etc/profile.d/aws_profile.sh'

# Exit after installation

echo -e "\n## Completed installation of:\n"
for app in $APPLICATIONS; do
  echo "--- $app";
done