FROM opensuse/leap

RUN zypper install -y  gcc make tar git wget nano gzip
RUN wget https://go.dev/dl/go1.20.4.linux-amd64.tar.gz && tar -xf go1.20.4.linux-amd64.tar.gz && mv go ~
RUN git clone https://github.com/ethereum/go-ethereum.git && cd go-ethereum && git checkout v1.11.6
RUN touch ~/.bashrc && echo "export PATH=/root/go/bin:/go-ethereum/build/bin/:$PATH;export GOPATH=/root/go" > ~/.bashrc && source ~/.bashrc && cd go-ethereum && make all
EXPOSE 8545
# CMD ["go-ethereum/build/bin/geth", "--cache=2048", "--http", "--http.addr=0.0.0.0", "--http.api=eth,web3,net,personal,miner", "--snapshot", "--http.vhosts=*", "--http.corsdomain=*", "--allow-insecure-unlock"]
