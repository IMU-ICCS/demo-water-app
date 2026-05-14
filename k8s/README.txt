
---------------------------------------
-- Preparation
---------------------------------------
cd k8s
kind  create cluster --config kind/config-3-nodes.yaml
---------------------------------------
docker compose up -d suricata
docker exec -it suricata suricata-update
docker compose down
---------------------------------------
--- TEST SURICATA ---
docker compose up -d suricata
docker exec -it suricata curl http://testmyids.com
// docker exec -it suricata tail -f /var/log/suricata/fast.log
docker compose down
---------------------------------------

---------------------------------------
-- Start demo
---------------------------------------
cd k8s
docker compose up -d suricata
helm install test .
---------------------------------------

---------------------------------------
-- Stop demo
---------------------------------------
cd k8s
docker compose down
helm uninstall test
kubectl delete ds/ems-client-daemonset cm/ems-client-configmap cm/monitoring-configmap
---------------------------------------

---------------------------------------
-- View logs and events
---------------------------------------
kubectl get pods
kubectl logs -f $(kubectl get pods -l "app.kubernetes.io/name=ems-server" -o jsonpath="{.items[0].metadata.name}")
kubectl logs -f $(kubectl get pods -l "app.kubernetes.io/name=suricata-log-processor" -o jsonpath="{.items[0].metadata.name}")

kubectl exec -it $(kubectl get pods -l "app.kubernetes.io/name=ems-server" -o jsonpath="{.items[0].metadata.name}") -- ./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% 'attack_probability'
docker exec -it suricata curl http://testmyids.com
EDIT VALUES IN suricata-log-processor/params.txt
---------------------------------------