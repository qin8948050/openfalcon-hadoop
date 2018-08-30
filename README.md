# Openfalcon监控Hadoop服务,目前支持监控集群整体情况,rm,nm,nn,jn
## 脚本目录说明

bin   //执行脚本  

conf  //配置监控指标  

data  //监控指标数据

## 脚本使用说明
 python ./bin/monitor-hadoop.py -h  
 
 Usage: python monitor-hadoop.py [option][value]...  
    -h or --help 
    
    -p or --port="service port"  
    
    -n or n="node name"  
    
    -s or --service="service name"


#### 1)生成监控指标配置文件
  配置文件名称：${node_name}_${service_name} 例如： NameNode_RpcDetailedActivityForPort
  
  python ./bin/monitor-hadoop.py -p 50070 -n NameNode -s RpcDetailedActivityForPort
#### 2)添加监控指标
    vim ./conf/NameNode_RpcDetailedActivityForPort
#### 3)执行监控任务
    python ./bin/monitor-hadoop.py -p 50070 -n NameNode -s RpcDetailedActivityForPort  


