#!/usr/bin/env python3
#
# This script downloads the updated list of VPN servers offered by proXPN and
# then lets you choose which one you want to establish the VPN connection to.
#
# In order to stop the VPN tunnel, use CTRL+c
#
# Call with "--help" for more info
#


import os.path
import xml.etree.ElementTree
import argparse
import sys


# This is the filename to retrieve from proXPN webpage that contains the updated
# list of VPN servers.
#
LOCATIONS_FILE_NAME     = "locations-v2.xml"

HOME                    = os.path.expanduser("~")
PROXPN_CONF_FOLDER      = HOME + "/.proxpn"
SERVERS_LIST_CACHE_FILE = PROXPN_CONF_FOLDER + "/" + LOCATIONS_FILE_NAME
SERVERS_LIST_URL        = "http://www.proxpn.com/updater/" + LOCATIONS_FILE_NAME
OPENVPN_CONF_FILE       = PROXPN_CONF_FOLDER + "/proxpn.ovpn"
CREDENTIALS_FILE        = PROXPN_CONF_FOLDER + "/auth.conf"


# Parse input arguments
#
parser = argparse.ArgumentParser(description='Stablish a connection with a proXPN server')
parser.add_argument('--force-download', '-f', action='count', help='Delete the servers XML cached file, forcing it to be re-downloaded from the proXPN web page')
parser.add_argument('--reset-credentials', '-r', action='count', help='Delete the auth file, so that you will be asked for username and passowrd once again')
parser.add_argument('--udp', '-u', action='count', help='Show only UDP servers')
parser.add_argument('--tcp', '-t', action='count', help='Show only TCP servers')

args = parser.parse_args()

if args.force_download:
    if os.path.exists(SERVERS_LIST_CACHE_FILE):
        os.remove(SERVERS_LIST_CACHE_FILE)

if args.reset_credentials:
    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)

show_udp_servers = True
show_tcp_servers = True
if args.udp and args.tcp:
    print("ERROR: You can only specify either '-u' or '-t', and not both at the same time")
    sys.exit(-1)
elif args.udp:
    show_tcp_servers = False
elif args.tcp:
    show_udp_servers = False


# Make sure the "~/.proxpn" folder exists.
# This folder contains the openvpn configuration file.
# It will be used to store a cached version of the "list of server" XML file
# (so that we don't have to download it each time we run the program)
#
if not os.path.exists(PROXPN_CONF_FOLDER) or not os.path.isfile(OPENVPN_CONF_FILE):
    print("ERROR: In order for this script to work, the following folder must exist: '"+
          PROXPN_CONF_FOLDER+"'. It must also contain a file named '"+OPENVPN_CONF_FILE+
          "', where all the openvpn connection parameters are listed. This file was "+
          "included with this script. It can also be obtained from the Windows installation "+
          "of the official proXPN client.")
    sys.exit(-1)

    
# If the cached XML file does not exist, download it from the proXPN server and
# save it
#
if not os.path.isfile(SERVERS_LIST_CACHE_FILE):

    import urllib.request

    response = urllib.request.urlopen(SERVERS_LIST_URL)
    text     = response.read().decode("utf-8")

    f = open(SERVERS_LIST_CACHE_FILE, "w")

    f.write(text)
    f.close()


# Now, parse it: for each location obtain its name, TCP and UDP addresses (only
# one of them might be available in some cases)
#
vpn_servers = []

e = xml.etree.ElementTree.parse(SERVERS_LIST_CACHE_FILE).getroot()
for location in e.findall(".//location"):
    name = location.find("name").text

    aux = location.find("openvpn")
    if aux != None:
        ip_tcp = aux.get("ip")
    else:
        ip_tcp = "NA"

    aux = location.find("openvpn-udp")
    if aux != None:
        ip_udp = aux.get("ip")
    else:
        ip_udp = "NA"

    vpn_servers.append((name, ip_tcp, ip_udp))


# Next, present the user with all the options and let them choose
#
print("List of available servers:")
options = []
number  = 0
for x in sorted(vpn_servers, key=lambda x:x[0]):
    if x[1] != "NA" and show_tcp_servers:
        number += 1
        options.append((number, "tcp", x[0], x[1]))
    if x[2] != "NA" and show_udp_servers:
        number += 1
        options.append((number, "udp", x[0], x[2]))

MAX_LINES = number//5 + 1
for i in range(MAX_LINES):
    if i < number:
        aux = ""
        for j in range((number-1)//MAX_LINES + 1):
            if i + j*MAX_LINES < number:
                x = options[i + j*MAX_LINES]
                aux += "*{:2d}* {:s} {:20s}".format(x[0], x[1], x[2])
        print(aux)


selected_option = int(input("Enter the server number: "))

if selected_option >= number:
    print("ERROR: Invalid option number")
    sys.exit(-1)

selected_server = [x for x in options if x[0]==selected_option][0]

# Ask for user and password and save them to the CREDENTIALS_FILE
#
print("")
if not os.path.isfile(CREDENTIALS_FILE):
    username = input("Username: ")
    password = input("Password: ")
    f = open(CREDENTIALS_FILE, "w")
    f.write(username+"\n")
    f.write(password+"\n")
    f.close()
    os.chmod(CREDENTIALS_FILE, 0o600)


# Establish the VPN connection
#
command = "sudo openvpn --config "+OPENVPN_CONF_FILE+" --remote "+selected_server[3]+" 443 "+selected_server[1]+" --auth-user-pass "+CREDENTIALS_FILE+" --auth-nocache"
print("")
print("This is the 'openvpn' command that we are going to execute:")
print(command)
print("")
input("If that's OK with you, press ENTER. Otherwise press CTRL+c")
    
os.system(command)


