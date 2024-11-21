# Command Sender
This is an interactive script which can send a single command to a device over SSH.  This is great for quick and simple validation of information.

## Prepping your host
This script leverages [paramiko](https://github.com/paramiko/paramiko) which you will need to install

    pip install paramiko

### Using the script
The script is simply run with the python command

    python3 CommandSender.py

Once run you will go through the interactive menu which will ask a few simple questions

    Enter the IP Address or FQDN of the device to connect to: <ip> or <fqdn>
    Enter the username to connect with: FOO
    Enter the password for the user: BAR
    Enter the command to send to the device: show version

The script will then run and output your command

    Connecting to 172.16.32.10...
    Executing command: show version
    Output:
    Arista CCS-720XP-24ZY4-F
    Hardware version: 11.21
    Serial number: A SERIAL NUMBER
    Hardware MAC address: SOME MAC
    System MAC address: SOME MAC
    
    Software image version: 4.31.5M
    <snip>
    
    Connection closed.
