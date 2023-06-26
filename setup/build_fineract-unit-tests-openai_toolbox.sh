#!/bin/bash

# Check that two parameters are passed.
if [ $# -ne 1 ] 
  then
    echo "This script requires one argument: <OPENAI_API_KEY>. A key can be"
    echo "from the OpenAI website, https://openai.com/"
    exit 1
fi

# Create container
NAME=fineract-unit-tests-openai
RUN="toolbox run --container $NAME"
toolbox rm --force $NAME || true
toolbox create --container $NAME

# Install applications
APPLICATIONS=" python3-pandas python3-javalang \
               cmake gcc-c++ blas-devel lapack-devel swig "

## Install applications
$RUN sudo dnf install -y $APPLICATIONS;

## Install Python packages
$RUN sudo pip install --upgrade -r requirements.txt

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
export OPENAI_API_KEY='$1' "\
> /etc/profile.d/api_secrets.sh'
