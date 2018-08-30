#!/usr/bin/env python
# -*- coding:utf-8 -*-
import getopt
import sys
import requests
import time
import json
import datetime
import  socket
import time
import re
import os
import hashlib

script_dir=os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),os.path.pardir))
now=datetime.datetime.now()
ts = int(time.mktime(now.timetuple()))
hostName = socket.gethostname()
hostIp=socket.gethostbyname(hostName)
MONITOR_TEMPLATE_VALUE = {
    "endpoint": hostName,
    "metric": "test-metric",
    "timestamp": ts,
    "step": 60,
    "value": 1,
    "counterType": "GAUGE",
    "tags": "Hadoop:service=NameNode,name=StartupProgress",
}


def monitor_cluster():
    metric_item_list=[]
    target_url="http://10.8.33.10:"+SERVICE_PORT+"/ws/v1/cluster/metrics"
    response = requests.request("GET", target_url).json()[SERVICE_NAME]
    MONITOR_DATA=[]
    with open('../conf/'+SERVICE_NAME,'r') as metric_item_key:
        for line in metric_item_key:
            metric_item_list.append(line.strip())
        MONITOR_TEMPLATE_VALUE["tags"] = "name="+SERVICE_NAME
        for i in metric_item_list:
            MONITOR_TEMPLATE_VALUE["metric"] = i
            MONITOR_TEMPLATE_VALUE["value"] = response[i]
            MONITOR_DATA.append(MONITOR_TEMPLATE_VALUE.copy())
    r = requests.post("http://10.8.132.147:1988/v1/push", data=json.dumps(MONITOR_DATA))
    MONITOR_DATA[:]=[]
    print(r.text)

class Hadoop_monitor:
    def __init__(self,port,node,service,level):
        self.port=port
        self.node=node
        self.service=service
        self.level=level
        self.conf_dir=script_dir+"/conf/"
        self.data_dir=script_dir+"/data/"
    def get_metric_url(self):
        original_url="http://10.8.130.10:{0}/jmx".format(self.port)
        response = requests.request("GET", original_url).json()["beans"]
        target_url_list=[]
        search_words=self.node+",name="+self.service
        for i in response:
            target_service_name=i["name"]
            if re.search(search_words,target_service_name):
                target_url = original_url + "?qry={0}".format(target_service_name)
                target_url_list.append(target_url)
        return target_url_list

    def get_metric_file_path_list(self,target_url_list):
        metric_file_path_list=[]
        metric_key_list=[]
        metric_key_file_path=self.conf_dir+self.node+"_"+self.service
        if not os.path.exists(metric_key_file_path):
            f_tmp=open(metric_key_file_path,"w")
            f_tmp.write("name")
            f_tmp.close()
        metric_item_key=file(metric_key_file_path,"r")
        for line in metric_item_key:
            metric_key_list.append(line.strip())
        for target_url in target_url_list:
            metric_file_path=self.data_dir+hashlib.md5(target_url.encode()).hexdigest()+'.json'
            metric_file_path_list.append(metric_file_path)
            response = requests.request("GET", target_url).json()["beans"][0]
            for metric_key in response.keys():
                if metric_key not in metric_key_list:
                    del(response[metric_key])
            with open(metric_file_path, "w") as metric_item_file:
                json.dump(response, metric_item_file)
        return metric_file_path_list

    def push_metric(self,metric_file_path_list):
        headers = {'content-type': 'application/json'}
        MONITOR_DATA=[]
        for i in metric_file_path_list:
            with open(i,'r') as f:
                metric_items=json.load(f)
                MONITOR_TEMPLATE_VALUE["tags"]=metric_items["name"]
                for monitor_key, monitor_value in metric_items.iteritems():
                    MONITOR_TEMPLATE_VALUE["metric"]=monitor_key
                    MONITOR_TEMPLATE_VALUE["value"]=monitor_value
                    MONITOR_DATA.append(MONITOR_TEMPLATE_VALUE.copy())
        r = requests.post("http://10.8.132.147:1988/v1/push",data=json.dumps(MONITOR_DATA))
        MONITOR_DATA[:]=[]
        print(r.text)


def usage():
    print('''Usage: python monitor-hadoop.py [option][value]...
    -h or --help
    -p or --port="service port"
    -n or n="node name"
    -s or --service="service name"
    -l or --level="leve info (defalut 2)"
    ''')
    return 0
def main():
    if SERVICE_NAME == "clusterMetrics":
        monitor_cluster()
    else:
        testa=Hadoop_monitor(SERVICE_PORT,NODE_NAME,SERVICE_NAME,LEVEL_NUM)
        target_url_list=testa.get_metric_url()
        metric_file_path_list=testa.get_metric_file_path_list(target_url_list)
        testa.push_metric(metric_file_path_list)

if "__main__" == __name__:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h-p:-n:-s:-l:", ["help", "port=","node=","service=","level="]);
        LEVEL_NUM=2
        for opt, arg in opts:
            if opt in ("-h","--help"):
                usage()
                sys.exit(0)
            elif opt in("-p","--port"):
                SERVICE_PORT=arg
                continue
            elif opt in("-n","--node"):
                NODE_NAME=arg
                continue
            elif opt in ("-s","--service"):
                SERVICE_NAME=arg
                continue
            elif opt in("-l","--level"):
                LEVEL_NUM=arg
                continue
        if not (SERVICE_PORT  or SERVICE_NAME):
            usage()
        main()
    except (getopt.GetoptError,NameError):
        usage()
        sys.exit(1)
