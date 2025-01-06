if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <gomaxprocs> <thrifty> <epaxos_enabled> <mencius_enabled> <sdpaxos_enabled>"
    exit 1
fi

gomaxprocs=$1
thrifty=$2
epaxos_enabled=$3
mencius_enabled=$4
sdpaxos_enabled=$5

# fill with master_ip (private) and machine_ip (private)
../bin/server -maddr "..." -addr "..." -p $gomaxprocs -thrifty=$thrifty -e=$epaxos_enabled -m=$mencius_enabled -n=$sdpaxos_enabled -port 7071 &