function install_python() {
    sudo apt update
    sudo apt install -y ${py_ver}
    sudo apt install -y ${py_ver}-pip
    ${py_ver} --version
}

# Installs a version of Golang since Rabia is written in Golang
function install_go() { 
    sudo apt install curl
    curl -OL https://golang.org/dl/${go_tar}
    sudo tar -C /usr/local -xzf ${go_tar}
    rm ${go_tar}
    echo 'export PATH=${PATH}:/usr/local/go/bin' >>~/.bashrc
    echo 'export GOPATH=$PWD' >>~/.bashrc
    echo 'export GO111MODULE="auto"' >>~/.bashrc
}

function main() {
    install_python
    install_go
}

go_tar=go1.20.linux-amd64.tar.gz
py_ver=python3
main
