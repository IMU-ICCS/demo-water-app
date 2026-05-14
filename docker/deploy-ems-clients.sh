#!/usr/bin/env bash

# Instruct EMS server to deploy EMS clients
declare -a arr=("vm1" "vm2" "vm3")

for vm in "${arr[@]}"; do
  echo "Installing EMS client at $vm"
  curl -s -k --request POST "https://localhost:8111/baguette/registerNode" --header "EMS-API-KEY: 1234567890" --header "Content-Type: application/json" --data "{ 'applicationId': '12345', 'id': '$vm', 'name': '$vm', 'operatingSystem': 'UBUNTU', 'address': '$vm', 'ssh': { 'port': '22', 'username': 'root', 'password': 'experiment' }, 'type': 'VM', 'provider': 'DOCKER' }"
done