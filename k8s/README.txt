
---------------------------------------
-- Preparation
---------------------------------------
cd k8s
kind  create cluster --config kind/config-3-nodes.yaml

---------------------------------------
-- Start demo
---------------------------------------
cd tests
docker compose up -d suricata
---------------------------------------
cd ../k8s
helm install test .
---------------------------------------
docker exec -it suricata curl http://testmyids.com

---------------------------------------
-- Stop demo
---------------------------------------
cd tests
docker compose down
---------------------------------------
cd ../k8s
helm uninstall test
---------------------------------------


---------------------------------------
-- View logs and events
---------------------------------------
kubectl logs -f test-ems-server-....
kubectl logs -f test-suricata-log-processor-....

kubectl exec -it test-ems-server-.... -- ./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% '>'