# boofuzz fuzzer
#
# $ docker run -it --rm --name boofuzz -v /home/user/boofuzz:/boofuzz -p 26000:26000 boofuzz

FROM debian:bullseye-slim

RUN apt-get update \
 && apt-get install -qqy \
    ca-certificates \
    git \
    gcc \
    g++ \
    make \
    libpcap-dev \
    tcl-dev \
    python3-pip \
    libpython3-dev \
    iputils-ping \    
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

RUN git clone https://github.com/igaritano/hping.git hping \
 ;  cd /hping \
 ;  ./configure \
 ;  make \
 ;  make install

RUN pip install --upgrade pip \
 ;  pip install pcapy

RUN git clone https://github.com/jtpereyda/boofuzz.git boofuzz \
 ;  mv boofuzz /opt/ \
 ;  cd /opt/boofuzz \
 ;  git checkout tags/v0.3.0 \
 ;  pip install .

WORKDIR /boofuzz

ENTRYPOINT ["bash"]
