import ipaddress
import subprocess
import datetime
import time
import re
from sys import platform
from threading import Thread

reachable = []                              #Empty list to collect reachable hosts
reachable_rtt = []                          #Empty list to collect reachable hosts + RTT
not_reachable = []                          #Empty list to collect unreachable hosts

def ping_test (ip):
    if "win32" in platform:                   #platform equals win32 for Windows, equals linux for Linux, darwin for Mac
        pingcount = "-n"
        pattern = r"Average = (\d+\S+)"
        pattern_ip = r"\[\d+.\d+.\d+.\d+\]"
        keyword = "Average"
        ping_test = subprocess.Popen(["ping", pingcount, "2", ip], stdout = subprocess.PIPE,stderr = subprocess.PIPE, shell=True)
    else:                                   #Linux & Mac
        pingcount = "-c"
        pattern = r"= \d+\.\d+/(\d+\.\d+)/\d+\.\d+/\d+\.\d+ ms"
        pattern_ip = r"\(\d+.\d+.\d+.\d+\)"
        keyword = "avg"
        ping_test = subprocess.Popen(["ping", pingcount, "2", ip], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    output = ping_test.communicate()[0]
    output_str = str(output)
    #print(output_str)
    if keyword in output_str:                #If Average latency is available, it's reachable
        try:
            ipaddress.ip_address(ip)           #Check if it's an IP address
            type = "ip"
        except ValueError:                      
            type = "hostname"
        rtt = re.findall(pattern, output.decode())[0]   #Regex to find latency
        if "linux" in platform or "darwin" in platform:                 
            rtt = rtt+"ms"
        if type == "ip":
            print("IP: {0:56} Average RTT: {1}".format(ip, rtt))
        else:                                   
            ipadd = re.findall(pattern_ip,output.decode())[0]       #if type is hostname, add resolved IP address
            print("Hostname: {0:50} Average RTT: {1}".format(ip+" "+ipadd,rtt))
        reachable.append(ip)
        reachable_rtt.append("{0:41} RTT:{1}".format(ip, rtt))
    else:
        not_reachable.append(ip)            #Else, it's not reachable

def main():
    date = datetime.date.today()
    start_time = time.time()                 
    f = open('hosts.txt','r')               #open file
    print("\nHostname/IP Address {0:40} Average Round Trip Times {1}".format("",""))
    print("-------------------------------------------------------------------------------------")
    thread_list = []                        
    count = 0                              #total address count
    for line in f:
        IP = line.strip()
        if "/" in IP:                     #If Address has subnet mask symbol(/), eg: 192.168.1.0/30
            for ip in ipaddress.IPv4Network(IP,False): 
                count += 1
                th = Thread(target=ping_test, args=(str(ip),))  
                th.start()
                thread_list.append(th)
        else:                             #Single IP address or hostname, instead of IP range
            count += 1
            th = Thread(target=ping_test, args=(IP,))   #args should be tuple, need extra comma when passing only 1 param
            th.start()
            thread_list.append(th)
    for th in thread_list:
        th.join()
    time_elapsed = time.time() - start_time            #calculate elapsed time
    print("-------------------------------------------------------------------------------------")
    print("Test completed! (It took %.2f seconds to test %d addresses.)\n" % (time_elapsed,count))
    print("Reachable:\n {} ".format(reachable))
    print("Not reachable:\n {}".format(not_reachable))

    with open('%s-Reachable.txt' % date, 'w') as f:
        for item in reachable:
            f.write("%s\n" % item)
    with open('%s-Reachable_RTT.txt' % date, 'w') as f:
        for item in reachable_rtt:
            f.write("%s\n" % item)
    with open('%s-Not_reachable.txt' % date, 'w') as f:
        for item in not_reachable:
            f.write("%s\n" % item)

    print("\nCheck txt files for complete results!\n")

if __name__ == "__main__":
    main()
