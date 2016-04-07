#!/usr/bin/python
### zabbix 3.0.1
### python 2.6.6
### scripts update zabbix database to change discovered host display name
### discovered host's default name is ip which is not user-friendly and recognizable
### this scripts will change ip to zabbix agent.hostname
import os
import mysql.connector
import re

# ip addr regex
pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

# connect to database
try:
    conn=mysql.connector.connect(host='localhost',user='zabbix',passwd='',db='zabbix')
    cur=conn.cursor()
    ### get discovered hostid and hostname in database
    cur.execute('''select hosts.hostid, hosts.host, hosts.name
                   from hosts_groups
                   inner join hosts
                   on hosts_groups.groupid=5 and hosts_groups.hostid=hosts.hostid and hosts.host=hosts.name;''')
    rows = cur.fetchall()
    if (len(rows) == 0): exit()
    for row in rows:
        hostid = row[0]
        ip = row[1]
        name = row[2]
        #check if hostname is an ip address
        #discovered VM's hostname is an UUID not an address
        if not pat.match(name): continue
        command = str("zabbix_get -s " + name + " -k agent.hostname")
        dhname = os.popen(command).readlines()[0].strip('\n')
        #update database
        update_sql = str("update hosts set host='" + dhname + "',name='" + dhname + "' where hostid='" + str(hostid) + "'")
        cur.execute(update_sql)
    cur.close()
    conn.commit()
    conn.close()
except mysql.connector.Error as err:
    print(err)
