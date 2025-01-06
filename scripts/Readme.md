Implementation details
======

# Amazon Setup
## Configurations
### Instance type
- t2.medium
    - 2 vCPU
    - 24 CPU Credits / hour
    - 4 GiB Memory
### Number of EC2 Instances (see below)
### Network settings (Security groups):
- system_security_group
    - Default VPC 
    - Inbound rule: All traffic && All ports && 0.0.0.0
    - Outbound rule: All traffic && All ports && 0.0.0.0
- allow all incoming and outgoing ports
    ```bash
    sudo ufw enable
    sudo ufw default allow incoming
    sudo ufw default allow outgoing
    sudo ufw reload
    ```
### OS: Ubuntu Linux

## Preserving the budget
- Start instances + associate an Elastic IP to each instance (remains the same IP address)
- Close running instances + release Elastip IP addresses
- "End lab" after work is done
- Use https://calculator.aws/#/ to estimate the cost

## Using SSH to Connect
- Step 1: Change the permissions in the pem file
 ```bash
cd ~/Downloads
chmod 400 aws_key_559.pem
 ```
- Step 2: **Instances** -> Click the instance -> *Descriptions* tab -> Copy the **IPv4 Public IP** value
- Step 3: Ssh to the chosen instance
 ```bash
ssh -i aws_key.pem ubuntu@public_ip
 ```

# Implementation
### Start plotting the Figure 9a and Figure 10 of SDPaxos.
### Prints a message when all client processes are finished

## Plot 9a (4 EC2 instances, 1 for the master + a server, 2 for servers and 1 for the client)
### Clients = 20 (minimum)
### Requests are 100% writes, 5000 (16KB-small) and 20000 (1KB-large)
#### Epaxos (epaxos_enabled=true and c=0 and thrifty-true), Mencius (epaxos_enabled=false and mencius_enabled=true) and Multi-Paxos (epaxos_enabled=false and mencius_enabled=false), SDPaxos (n=true else false)
- run_master **replicas** **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_master.sh 3 4 false true false false
 ```
- run_server **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_server.sh 4 false true false false
 ```
- run_client **replicas** **clients** **requests** **writes** **epaxos_enabled** **GOMAXPROCS** **conflicts** **filename** <br>
 ```bash
# Modify clients epaxos_enabled conflicts filename
./run_client.sh 3 20 20000 100 true 4 0 epaxos0
 ```

### Plot 10a (4 EC2 instances, 1 for the master + a server, 2 for servers and 1 for the client)
### Clients = 20 (minimum)
### Requests are 100% writes, 5000 (16KB-small) and 20000 (1KB-large)
### c = 0, 5, 25, 50, 75, 100
#### Epaxos (epaxos_enabled=true and thrifty-true), SDPaxos (n=true else false)
- run_master **replicas** **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_master.sh 3 4 false true false false
 ```
- run_server **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_server.sh 4 false true false false
 ```
- run_client **replicas** **clients** **requests** **writes** **epaxos_enabled** **GOMAXPROCS** **conflicts** **filename** <br>
 ```bash
# Modify clients epaxos_enabled conflicts filename
./run_client.sh 3 20 20000 100 true 4 50 epaxos0
 ```

### Plot 10b (6 EC2 instances, 1 for the master + a server, 4 for servers and 1 for the client)
### Clients = 20 (minimum)
### Requests are 100% writes, requests are 16B and 1KB -> 5000 and 20000
### c = 0, 5, 25, 50, 75, 100
#### Epaxos (epaxos_enabled=true and thrifty-true), SDPaxos (n=true else false)
- run_master **replicas** **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_master.sh 5 4 false true false false
 ```
- run_server **gomaxprocs** **thrifty** **epaxos_enabled** **mencius_enabled** **sdpaxos_enabled** <br>
 ```bash
# Modify epaxos_enabled mencius_enabled
./run_server.sh 4 false true false false
 ```
- run_client **replicas** **clients** **requests** **writes** **epaxos_enabled** **GOMAXPROCS** **conflicts** **filename** <br>
 ```bash
# Modify clients epaxos_enabled conflicts filename
./run_client.sh 5 20 20000 100 true 4 50 epaxos0
 ```

Analyze the results in the `logs/` folder and create the plots:
```
python3 create_plots.py 
```