if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <replicas> <gomaxprocs> <thrifty> <epaxos_enabled> <mencius_enabled> <sdpaxos_enabled>"
    exit 1
fi

replicas=$1
gomaxprocs=$2
thrifty=$3
epaxos_enabled=$4
mencius_enabled=$5
sdpaxos_enabled=$6

#fill with master_ip (private) and machine_ip (private)
../bin/master -N $replicas &
sleep 0.1
../bin/server -maddr "..." -addr "..." -p $gomaxprocs -thrifty=$thrifty -e=$epaxos_enabled -m=$mencius_enabled -n=$sdpaxos_enabled &