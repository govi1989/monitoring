#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import socket
import pika

def config():
    with open('configuration/common_config.json') as json_data_file:
        data = json.load(json_data_file)
    return(data)

def get_hostname():
    try:
        myname = socket.getfqdn(socket.gethostname( ))
    except Exception as excp:
        print(excp)
    else:
        return(myname)

def check_queue(mqconfig):
    mqhost=mqconfig['host']
    mquser=mqconfig['user']
    mqpass=mqconfig['password']
    mqport=mqconfig['port']
    qcount={}
    pika_conn_params = pika.ConnectionParameters(
        host=mqhost, port=mqport,
        credentials=pika.credentials.PlainCredentials(mquser, mqpass),
    )
    connection = pika.BlockingConnection(pika_conn_params)
    channel = connection.channel()
    for mqueue in mqconfig['queues']:
        queue = channel.queue_declare(
            queue=mqueue, durable=True,
            exclusive=False, auto_delete=False
        )
        qcount[mqueue] = queue.method.message_count
    connection.close()
    return(qcount)

def validate_queue(queues,qcount):
    result=""
    sev=None
    for q in queues:
        warn=queues[q][0]
        critical=queues[q][1]
        if warn <= qcount[q]:
           if critical <= qcount[q]:
                result += "\nQueue %s - Critical. Current Queue - %s" %(q, qcount[q])
                sev="red"
           
           else:
                result += "\nQueue %s - Warning. Current Queue - %s" %(q, qcount[q])
                if sev is None:
                    sev="yellow"
        else:
            result += "\nQueue %s - Normal. Current Queue - %s" %(q, qcount[q])
    return(result, sev)

if __name__ == '__main__':
    data=config()
    qcount = check_queue(data['mq'])
    queues = data['mq']['queues']
    result, sev = validate_queue(queues,qcount)
    print(sev)
    print(result)
