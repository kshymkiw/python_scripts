# Arista Switch Information
A simple script designed to be flexible enough to modify.  This script leverages the Arista eAPI[^1] and is written in Python.

## Prepping your Arista switches
Out of the box, this script will **not** work since it leverages the on box eAPI. You need to make a few config changes to be able to use this script.

    Arista> enable
    Arista# configure terminal
    Arista(config)# management api http-commands
    Arista(config-mgmt-api-http-cmds)# [no] shutdown

This will enable eAPI via `https`  If you desire for whatever reason to use `http` instead you will also need to add

    Arista(config-mgmt-api-http-cmds)#  protocol http

If you leverage a management VRF you will also need to add support for that VRF and `no shut` that config

    Arista(config-mgmt-api-http-cmds)#  vrf FOO
    Arista(config-mgmt-api-http-cmds-vrf-FOO)#  [no] shutdown

### Prepping your host
This script uses a library [jsonrpclib](https://github.com/joshmarshall/jsonrpclib) which you will need to install

    pip install jsonrpclib

#### Using the script
Using the script is as simple as it should be.  Dwonload the script or `git clone` this repository.  Once there invoke the script

    root@server:/home$ python3 switch_info.py 192.168.1.1 --username FOO --password BAR

Or if you want to read from a file

    root@server:/home$ python3 switch_info.py --username FOO --password BAR /path/to/file/switches.txt

The script should print to your terminal session the following

    Processing the following switches: 172.16.32.15
    ----- Data for 172.16.32.15 -----
    Hostname: houseswitch
    Version: 4.31.5M
    MAC Address: c0:69:11:51:24:49
    VLAN Information:
        VLAN 1 - Dynamic: 0, Unicast: 0, Multicast: 0
        VLAN 3 - Dynamic: 25, Unicast: 0, Multicast: 0
        VLAN 100 - Dynamic: 4, Unicast: 0, Multicast: 0
    Routing Information:
        Connected Routes: 0
        Static Routes: 0
        Internal Routes: 3
        OSPF Intra Area: 0
        OSPF External Type 1: 0
        BGP External Routes: 0
        BGP Internal Routes: 0

##### Updates
This is a work in progress script.  Things I would like to add
1.  ~~Ability to read in a text or csv file with multiple hosts~~
2.  Ability to embed username and password or possibly certificate based
3.  Ability to loop this to loop to run every `x` seconds/minutes/hours/days
4.  Cleanup and optimize
5.  Enhance error handling

[^1] Information about the [Arista eAPI](https://arista.my.site.com/AristaCommunity/s/article/arista-eapi-101)
