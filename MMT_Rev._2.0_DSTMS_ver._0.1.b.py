# -*- coding: utf-8 -*-

# Modules
# API miner
import socket
# JSON
import json
# Scheduler
import schedule
# Date time
import datetime
import time
# Config
import configparser

# Global variable
global Host, Tr_CH
global tmp_file_miner, file_path, file_path_collector

# Name of test files
tmp_file_miner = '1-temp-miner.log'
file_path = '2-info.log'
file_path_collector = '3-collector-info.log'

# Import configuration from file
conf = configparser.RawConfigParser()
conf.read("config")

if conf.has_option("sys","Host"):
    Host = conf.get("sys","Host")

if conf.has_option("sys","Tr_CH"):
    Tr_CH = conf.getint("sys","Tr_CH")

# Function for interaction with DSTM's
def get_dstms():
    rig_name_ip_port = list(map(str, Host.split(';')))
    for x,i in enumerate(rig_name_ip_port):
        host_name_ip = i.split('@')
        host_name = host_name_ip[0]
        host_ip_port = str(host_name_ip[1])
        rig_ip_port = list(map(str, host_ip_port.split(':')))
        ip = rig_ip_port[0]
        port = int(rig_ip_port[1], 10)
        api_dstms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(str(datetime.datetime.now()), '-', 'Request for this host -', host_ip_port)
        try:
            api_dstms.connect((ip, port))
            request = '{"id":1, "method":"getstat"}'
            api_dstms.send(request.encode("utf-8"))
            response = api_dstms.recv(2048)
            api_dstms.close()
            api_data = json.loads(response.decode("utf-8"))
            print(str(datetime.datetime.now()),'-','Request for this host -',host_ip_port)
            print(str(datetime.datetime.now()), '-', 'Result request -', api_data)

        except TimeoutError as err:
            api_dstms.close()
            api_data = '{"State":"RIG is OFF, "ERROR":"Timeout ERROR"}'
            print(str(datetime.datetime.now()), '-', 'Result request -', api_data)

        except ConnectionRefusedError as err:
            api_dstms.close()
            api_data = '{"State":"RIG is OFF, "ERROR":"Connection Refused ERROR"}'
            print(str(datetime.datetime.now()), '-', 'Result request -', api_data)

        except:
            api_dstms.close()
            api_data = '{"State":"RIG is OFF, "ERROR":"Another ERROR"}'
            print(str(datetime.datetime.now()), '-', 'Result request -', api_data)

        # Write to file
        with open(tmp_file_miner, 'w', encoding='utf-8') as file:
            data_to_file = str(datetime.datetime.now()) + ' - ' + str(api_data) + '\n'
            file.write(data_to_file)

        # Write to file
        with open(file_path, 'a', encoding='utf-8') as file:
            data_to_file = str(datetime.datetime.now()) + ' - Host name - ' + host_name + ' - Host address - ' + host_ip_port + ' - ' + str(api_data)+ '\n'
            file.write(data_to_file)

        # Write to file
        with open(file_path_collector, 'a', encoding='utf-8') as file:
            data_to_file = str(api_data) + '\n'
            file.write(data_to_file)

# Call function
get_dstms()

# Scheduler for function
schedule.every(Tr_CH).minutes.do(get_dstms)

# Program loop
while True:
    schedule.run_pending()
    time.sleep(1)

