if [ "$#" -ne 8 ]; then
    echo "Usage: $0 <replicas> <clients> <requests> <writes> <epaxos_enabled> <GOMAXPROCS> <conflicts> <filename>"
    exit 1
fi

replicas=$1
clients=$2
reqs=$3
writes=$4
epaxos_enabled=$5
gomaxprocs=$6
conflicts=$7
rounds=$((reqs / 1))

# fill with master_ip (private)
for((c = 0; c < $clients; c++))
do
    filename=logs-$replicas-replicas-$8/$8-S$replicas-C$clients-r$reqs-b$batch_size-c$conflicts--client$c.out
    ../bin/client -maddr "..." -q $reqs -w $writes -e=$epaxos_enabled -f=$fast_paxos_enabled -r $rounds -p $gomaxprocs -c $conflicts >> $filename &
done
./check_process_finished.sh