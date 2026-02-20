
---------------------------------------
cd tests
docker compose up
---------------------------------------
docker exec -it vm1 bash
cd /app
java -jar target/suricata-alert-streamer-1.0.0.jar
---OR--
cd /app/python
source venv/bin/activate
python3 suricata-alert-publisher.py
---------------------------------------
docker exec -it vm1 bash
cd /root/baguette-client/
./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% alerts
---------------------------------------
docker exec -it ems bash
./bin/client.sh receive -Uaaa -P111 tcp://localhost:61616?%KAP% '>'
---------------------------------------
docker exec -it suricata bash
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
