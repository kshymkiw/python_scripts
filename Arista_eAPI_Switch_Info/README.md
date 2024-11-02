# Arista Switch Information
A simple script designed to be flexible enough to modify.  This script leverages the Arista eAPI[^1] and is written in Python.

## Prepping your Arista switches
Out of the box, this script will not work since it leverages the on box eAPI. You need to make a few config changes to be able to use this script.

    Arista> enable
    Arista# configure terminal
    Arista(config)# management api http-commands
    Arista(config-mgmt-api-http-cmds)# [no] shutdown

This will enable eAPI via `https`  If you desire for whatever reason to use `http` instead you will also need to add

    Arista(config-mgmt-api-http-cmds)#  protocol http

If you leverage a management VRF you will also need to add support for that VRF and `no shut` that config

    Arista(config-mgmt-api-http-cmds)#  vrf <MANAGEMENT>
    Arista(config-mgmt-api-http-cmds-vrf-FOO)#  [no] shutdown

### Using the script
Using the script is as simple as it should be.  Dwonload the script or `git clone` this repository.  Once there invoke the script

    root@server:/home$ python3 switch_info.py 192.168.1.1 --username FOO --password BAR

The script should print to your terminal session

    Hello, my name is:  houseswitch
    My MAC address is:  somemacaddress
    My Version is:  4.31.5M
    VLAN-ID 1 has 0 dynamically learned MAC addresses, 0 learned unicast addresses and 0 multicast addresses
    VLAN-ID 3 has 27 dynamically learned MAC addresses, 0 learned unicast addresses and 0 multicast addresses
    VLAN-ID 100 has 2 dynamically learned MAC addresses, 0 learned unicast addresses and 0 multicast addresses
    Switch Route Information
    
    Connected Routes: 0
    Static Routes: 0
    Internal Routes: 3
    
    OSPF Routes
    Intra Area Routes: 0
    Inter Area Routes: 0
    External Type 1's: 0
    External Type 2's: 0
    NSSA External Type 1's: 0
    NSSA External Type 2's: 0
    
    BGP Routes
    eBGP Routes: 0
    iBGP Routes: 0
    Total BGP Routes: 0
    
    ISIS Routes
    Level1 Routes: 0
    Level2 Routes: 0
    Total ISIS Routes: 0
    
    Total Routes For This Switch: 3


#### Updates
This is a work in progress script.  Things I would like to add
1.  Ability to read in a text or csv file with multiple hosts
2.  Ability to embed username and password or possibly certificate based
3.  Ability to loop this to loop to run every `x` seconds/minutes/hours/days
4.  Cleanup and optimize where i can
5.  Enhance error handling

[^1] Information about the [Arista eAPI](https://arista.my.site.com/AristaCommunity/s/article/arista-eapi-101)
