import jsonrpclib
import sys
import os
import argparse
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger()

# Create stream handler for readable output
console_handler = logging.StreamHandler()

# Strip timestamps and logging level for console output
formatter = logging.Formatter('%(message)s') # Only print the message w/o extra detail
console_handler.setFormatter(formatter)

# Add console handler
logger.addHandler(console_handler)

# Set default logging level to INFO (DEBUG/ERROR can also be used)
logger.setLevel(logging.INFO)

def log_file(log_to_file):
    if log_to_file:
        log_handler = RotatingFileHandler('debug.log', maxBytes=5 * 1024 * 1024, backupCount=5)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(log_handler)

def create_server(url, username, password):
    """Create and return an RPC server object."""
    try:
        server = jsonrpclib.Server(url)
        server.runCmds(1, ["enable"])  # Can we enable ourselves?
        return server
    except jsonrpclib.ProtocolError as e:
        logger.error(f"Protocol error with {url}: {e}")
    except Exception as e:
        logger.error(f"Error with {url}: {e}")
    return None

def getEndpoints(switchHostnames, protocol, username, password):
    """Get API endpoints for switches."""
    apiEndpoints = {}
    for switch in switchHostnames:
        url = f"{protocol}://{username}:{password}@{switch}/command-api"
        server = create_server(url, username, password)
        if server:
            apiEndpoints[switch] = server
        else:
            logger.error(f"Skipping {switch} due to an  error.")
    return apiEndpoints

def getIPSfromfile(file_path):
    """Read IPs from a txt file."""
    try:
        with open(file_path, 'r') as file:
            ip_list = [line.strip() for line in file.readlines() if line.strip()]
        return ip_list
    except FileNotFoundError:
        logger.error(f"File Not Found: {file_path}")
    except Exception as e:
        logger.error(f"Error reading the file '{file_path}': {e}")
    return []

def fetchDatafromswitch(switchHostnames, protocol, username, password, selected_commands):
    """Fetch data from the switches."""
    endpointData = {}
    for switch in switchHostnames:
        url = f"{protocol}://{username}:{password}@{switch}/command-api"
        server = create_server(url, username, password)
        if not server:
            continue

        # Init switch_data dict
        switch_data = {}

        # Fetch data in batch or individual commands
        responses = [
            ("show hostname", "hostname"),
            ("show version", "version"),
            ("show mac address-table count", "mac address"),
            ("show ip route summary", "ip route")
        ]

        # Print output for each switch
        logger.info(f"----- Data for {switch} -----")
        for cmd, key in responses:
            if cmd in selected_commands:
                try:
                    response = server.runCmds(1, [cmd])
                    if cmd == "show hostname":
                        hostname = response[0].get("hostname", "Unknown")
                        logger.info(f"Hostname: {hostname}")
                        switch_data["hostname"] = hostname
                    elif cmd == "show version":
                        version_info = response[0]
                        version = version_info.get("version", "Unknown")
                        system_mac = version_info.get("systemMacAddress", "Unknown")
                        logger.info(f"Version: {version}")
                        logger.info(f"MAC Address: {system_mac}")
                        switch_data["version"] = version
                        switch_data["systemMacAddress"] = system_mac
                    elif cmd == "show mac address-table count":
                        vlan_counts = response[0].get("vlanCounts", {} )
                        if vlan_counts:
                            logger.info(f"VLAN Information:")
                            for vlan_id, counts in vlan_counts.items():
                                dynamic_count = counts.get("dynamic", 0)
                                unicast_count = counts.get("unicast", 0)
                                multicast_count = counts.get("multicast", 0)
                                logger.info(f"  VLAN {vlan_id} - Dynamic: {dynamic_count}, Unicast: {unicast_count}, Multicast: {multicast_count}")
                        else:
                            logger.info("No VLAN data available.")
                    elif cmd == "show ip route summary":
                        route_counts = response[0] if isinstance(response[0], dict) else {}
                        if route_counts:
                            logger.info(f"Routing Information:")
                            connected_count = route_counts.get("connected", 0)
                            static_count = route_counts.get("static", 0)
                            internal_routes = route_counts.get("internal", 0)
                            ospf_intra_area = route_counts.get("ospfIntraArea", 0)
                            ospf_external_1 = route_counts.get("ospfExternal1", 0)
                            bgp_external_count = route_counts.get("bgpExternal", 0)
                            bgp_internal_count = route_counts.get("bgpInternal", 0)

                            logger.info(f"  Connected Routes: {connected_count}")
                            logger.info(f"  Static Routes: {static_count}")
                            logger.info(f"  Internal Routes: {internal_routes}")
                            logger.info(f"  OSPF Intra Area: {ospf_intra_area}")
                            logger.info(f"  OSPF External Type 1: {ospf_external_1}")
                            logger.info(f"  BGP External Routes: {bgp_external_count}")
                            logger.info(f"  BGP Internal Routes: {bgp_internal_count}")
                        else:
                            logger.info("No route data available.")
                except jsonrpclib.ProtocolError as e:
                    logger.error(f"Error with {switch} (Command: {cmd}): {e}")
                except Exception as e:
                    logger.error(f"Error fetching data from {switch} (Command: {cmd}): {e}")
            # Store Switch Data
            if switch_data:
                endpointData[switch] = switch_data

        return endpointData

def parse_args():
    parser = argparse.ArgumentParser(description="Grab Information about Arista Switches")
    parser.add_argument("switches", metavar="SWITCH", nargs="*", help="Hostname or IP Address of your switch. Alternatively, specify a txt file")
    parser.add_argument("--ip-file", type=str, help="Path to a file containing a list of IP addresses.")
    parser.add_argument("--username", help="Username to connect", default="admin")
    parser.add_argument("--password", help="Users Password")
    parser.add_argument("--https", help="Use HTTPS instead of HTTP", action="store_const", const="https", default="http")
    parser.add_argument("--no-log", help="Disable logging", action="store_true")

    args = parser.parse_args()

    if args.ip_file:
        ip_list = getIPSfromfile(args.ip_file)
        return ip_list, args.https, args.username, args.password
    elif args.switches:
        return args.switches, args.https, args.username, args.password
    else:
        logger.error("No switches or IP addresses provided.")
        sys.exit(1)

def menu():
    print("\nSelect data you want to see:")
    print("1. Hostname")
    print("2. EOS Version")
    print("3. MAC Address Table")
    print("4. IP Route Summary")
    print("5. All Data")
    print("0. Exit")

    selected_commands = []
    while True:
        choice = input("Enter your option, 0 to exit:\n")
        if choice == '0':
            break
        elif choice == '1':
            selected_commands.append("show hostname")
        elif choice == '2':
            selected_commands.append("show version")
        elif choice == '3':
            selected_commands.append("show mac address-table count")
        elif choice == '4':
            selected_commands.append("show ip route summary")
        elif choice == '5':
            selected_commands.extend(["show hostname", "show version", "show mac address-table count", "show ip route summary"])
        else:
            print("Invalid choice, try again")
            continue
        # Execute the selected command immediately
        if selected_commands:
            return selected_commands

def main():
    switches, https, username, password = parse_args()

    if switches:
        logger.info(f"Processing the following switches: {', '.join(switches)}")
        selected_commands = menu() # Get the data
        if selected_commands:
            endpointData = fetchDatafromswitch(switches, https, username, password, selected_commands)
            # Grab the hostname to print
            for switch, data in endpointData.items():
                if isinstance(data, dict):
                    hostname = data.get("hostname", "Unknown")
                    logger.info(f"Hostname for {switch}: {hostname}")
                else:
                    logger.error(f"Unexpected data from {switch}")
    else:
        logger.error("No valid switches or IP addresses provided.")

if __name__ == "__main__":
    main()

