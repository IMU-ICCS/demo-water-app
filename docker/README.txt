
---------------------------------------
# Starts EMS server and deploys EMS clients to vm1,vm2,vm3
cd tests
docker compose up
---------------------------------------
# # Starts suricata-to-EMS bridge (alerts publisher)
# docker exec -it vm1 bash
# cd /app
# java -jar target/suricata-alert-streamer-1.0.0.jar
---------------------------------------
# Starts suricata-to-EMS bridge (alerts publisher)
docker exec -it vm1 bash
    ---RUN ONLY ONCE---
    apt update
    apt install -y python3.12-venv
    python3 -m venv /app/python/venv
    source venv/bin/activate
    pip3 install -r requirements.txt
---MAIN---
cd /app/python
source venv/bin/activate
python3 suricata-alert-publisher.py
---------------------------------------
# Starts a dummy Prometheus endpoint
docker exec -it vm1 bash
cd /app/python
source venv/bin/activate
python3 simple-prometheus-exporter.py
---------------------------------------
# Monitor EMS client events at vm1
docker exec -it vm1 bash
cd /root/baguette-client/
./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% alerts
---------------------------------------
# Monitor EMS server events
docker exec -it ems bash
./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% '>'
---------------------------------------
# Trigger alerts
docker exec -it suricata bash
---RUN ONLY ONCE--
suricata-update
restart
---TRIGGER ALERTS---
curl http://testmyids.com
---------------------------------------


===============================================================================
===============================================================================

---------------------------------------
docker run --rm -it --net=host \
    --name suricata \
    --cap-add=net_admin --cap-add=net_raw --cap-add=sys_nice \
	-v suricata_logs:/var/log/suricata \
	-v $(pwd)/lib:/var/lib/suricata \
	-v $(pwd)/etc:/etc/suricata \
    jasonish/suricata:8.0.3 -i eth0
---------------------------------------
cd ems-paper
docker compose up

docker-compose.yml:
  vm1:
    volumes:
      - /f/NTUA/CIPHER/CODE/eve-test-app:/app
      - suricata_logs:/app/logs
volumes:
  suricata_logs:
    external: true
---------------------------------------
docker exec -it vm1 bash
cd /app
java -jar target/suricata-alert-streamer-1.0.0.jar
---------------------------------------
docker exec -it vm1 bash
cd /root/baguette-client/
./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% alerts
---------------------------------------
docker exec -it suricata bash
curl http://testmyids.com
---------------------------------------

===============================================================================
===============================================================================

docker run --rm -it --net=host \
    --name suricata \
    --cap-add=net_admin --cap-add=net_raw --cap-add=sys_nice \
	-v $(pwd)/logs:/var/log/suricata \
	-v $(pwd)/lib:/var/lib/suricata \
	-v $(pwd)/etc:/etc/suricata \
    jasonish/suricata:8.0.3 -i eth0


jq 'select(.event_type=="alert") |
{
  timestamp,
  src_ip,
  src_port,
  dest_ip,
  dest_port,
  proto,
  signature: .alert.signature,
  signature_id: .alert.signature_id,
  severity: .alert.severity
}' /var/log/suricata/eve.json

tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert") |
{
  timestamp,
  src_ip,
  src_port,
  dest_ip,
  dest_port,
  proto,
  signature: .alert.signature,
  signature_id: .alert.signature_id,
  severity: .alert.severity
}'
