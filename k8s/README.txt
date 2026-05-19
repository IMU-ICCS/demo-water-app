
---------------------------------------
-- Preparation
---------------------------------------
Build and push 'suricata-log-processor' image
cd suricata-log-processor
docker build -t ....../suricata-log-processor .
docker push ....../suricata-log-processor:latest
---------------------------------------
Build and push 'streamlit-chart' image
cd streamlit-chart
docker build -t ....../streamlit-chart .
docker push ....../streamlit-chart:latest
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
# After EMS server is up and running
docker compose up -d streamlit-chart
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
kubectl logs -f $(kubectl get pods -l "app.kubernetes.io/name=water-flow-monitor" -o jsonpath="{.items[0].metadata.name}")

kubectl exec -it $(kubectl get pods -l "app.kubernetes.io/name=ems-server" -o jsonpath="{.items[0].metadata.name}") -- ./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% 'attack_probability'
docker exec -it suricata curl http://testmyids.com
EDIT VALUES IN suricata-log-processor/params.txt

ALSO VIEW chart at http://localhost:8501
---------------------------------------