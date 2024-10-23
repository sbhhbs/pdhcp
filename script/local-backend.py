#!/usr/bin/env python

import sys, json, time, os, datetime, traceback

log_id = 0

pool_assign_count = 0

static_mac_ip_map = {
    "90:09:D0:6C:53:95": {
        "host": "David1821",
        "addr": "10.65.2.12",
    },
}

dynamic_mac_ip_map = {

}

def check_ip_in_use(ip):
    if ip in dynamic_mac_ip_map.values():
        return True
    if ip in [x.get("addr") for x in static_mac_ip_map.values()]:
        return True
    return False

while True:
    try:
        request = json.loads(sys.stdin.readline())
        msgtype = request.get('dhcp-message-type', '')
        if msgtype == 'discover' or msgtype == 'request':
            preferred_ip:str = request.get("requested-ip-address")
            
            mac_address = request.get('client-hardware-address', '')

            assigned_ip = None

            if static_mac_ip_map.get(mac_address):
                assigned_ip = static_mac_ip_map.get(mac_address, {}).get("addr")

            if not assigned_ip:
                if dynamic_mac_ip_map.get(mac_address) == preferred_ip:
                    assigned_ip = preferred_ip
                elif preferred_ip and preferred_ip.startswith('10.65.') and check_ip_in_use(preferred_ip) == False:
                    assigned_ip = preferred_ip
            if not assigned_ip:
                def gen_ip_in_pool():
                    global pool_assign_count
                    pool_assign_count += 1
                    digit_3 = pool_assign_count // 255 + 200
                    digit_4 = pool_assign_count % 255
                    if digit_4 == 0:
                        digit_4 = 1
                    maybe_ip = f"10.65.{digit_3}.{digit_4}"
                    if pool_assign_count > 10000:
                        pool_assign_count = 0
                    return maybe_ip
                
                assigned_ip = gen_ip_in_pool()

                while check_ip_in_use(assigned_ip):
                    assigned_ip = gen_ip_in_pool()
                
            dynamic_mac_ip_map[mac_address] = assigned_ip
            response = {
                'dhcp-message-type':       'offer' if msgtype == 'discover' else 'ack',
                'client-hardware-address': mac_address,
                'bootp-transaction-id':    request.get('bootp-transaction-id', ''),
                'bootp-assigned-address':  assigned_ip,
                'subnet-mask':             '255.255.0.0',
                'routers':                 [ '10.65.0.1' ],
                'domain-name-servers':     [ '10.65.0.1' ],
                'domain-name':             'lan',
                'address-lease-time':      300,
                'bootp-server-address':    '10.65.0.1',
            }
            try:
                with open(f"/script/logs/{datetime.datetime.now()}_{log_id}.json", "w") as f:
                    json.dump({
                        "req": request,
                        "resp": response,
                        "_internal": {
                            "dynamic_mac_ip_map": dynamic_mac_ip_map,
                            "pool_assign_count": pool_assign_count,
                        }
                    }, f, indent=2, ensure_ascii=False)
                    log_id += 1
            except Exception as e:
                ...
            if os.environ.get("DHCP_BACKUP"):
                time.sleep(10)
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
    except Exception as e:
        with open(f"/script/logs/exception_{datetime.datetime.now()}_{log_id}.json", "w") as f:
            json.dump({
                "exc": str(e),
                "trace": traceback.format_exc(),
                "_internal": {
                    "dynamic_mac_ip_map": dynamic_mac_ip_map,
                    "pool_assign_count": pool_assign_count,
                }
            }, f, indent=2, ensure_ascii=False)
        break
