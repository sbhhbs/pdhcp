#!/usr/bin/env python

import sys, json, time

count = 0

while True:
    try:
        request = json.loads(sys.stdin.readline())
        msgtype = request.get('dhcp-message-type', '')
        if msgtype == 'discover' or msgtype == 'request':
            filename = 'ipxe.efi' if request.get('client-system', 0) == 7 else 'undionly.kpxe'
            if request.get('user-class') == 'iPXE':
                filename = 'http://192.168.40.1/ipxe.php?mac=${net0/mac}'
            response = {
                'dhcp-message-type':       'offer' if msgtype == 'discover' else 'ack',
                'client-hardware-address': request.get('client-hardware-address', ''),
                'bootp-transaction-id':    request.get('bootp-transaction-id', ''),
                'hostname':                'pdhcp',
                'bootp-assigned-address':  request.get('bootp-client-address', '192.168.40.150'),
                'subnet-mask':             '255.255.0.0',
                'routers':                 [ '10.65.0.1' ],
                'domain-name-servers':     [ '10.65.0.1' ],
                'domain-name':             'domain.com',
                'address-lease-time':      300,
                'bootp-server-address':    '10.65.0.1',
                'bootp-filename':          filename
            }
            with open(f"{count}.json", "w") as f:
                json.dump({
                    "req": request,
                    "resp": response
                }, f)
            time.sleep(10)
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
    except:
        break
