#!/bin/bash

# Check that two parameters are passed.
if [ $# -ne 2 ] 
  then
    echo "This script requires two arguments: <OPENAI_API_KEY> and <API_SECRET>."
    echo "The first is available from the OpenAI website and the latter is your"
    echo "own value to be used as an API password."
    exit 1
fi

# Create container
NAME=breakfree-dk-with-openai-chat
RUN="toolbox run --container $NAME"
toolbox rm --force $NAME || true
toolbox create --container $NAME

# Install applications
APPLICATIONS=" pandoc poppler-utils python3-pandas \
               cmake gcc-c++ blas-devel lapack-devel swig "

## Install applications
$RUN sudo dnf install -y $APPLICATIONS;

## Install Python packages
$RUN sudo pip install -r requirements.txt

## Install FAISS
$RUN bash -c 'cd /tmp; \
      git clone https://github.com/facebookresearch/faiss.git; \
      cd ./faiss; \
      cmake -DFAISS_ENABLE_GPU=OFF -DBUILD_TESTING=OFF -B build . ;\
      make -C build -j faiss;\
      make -C build -j swigfaiss; \
      sudo make -C build install; \
      (cd build/faiss/python && sudo python3 setup.py install) '

## Add API secrets to profile.d directory
$RUN sudo bash -c 'echo -e "\
export OPENAI_API_KEY='$1' \n\
export API_SECRET='$2' "\
> /etc/profile.d/api_secrets.sh'
