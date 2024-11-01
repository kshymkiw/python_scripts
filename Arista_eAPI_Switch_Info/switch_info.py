import json
import os
import sys
import argparse
import jsonrpclib

# EAPI script to print useful information about Arista Switches

def getEndpoints(switchHostnames, protocol, username, password):
    """ Check switch is up, and return information """
    apiEndpoints ={} # mapping from hostname to API Endpoint
    for switch in switchHostnames:
        url = "{protocol}://{user}:{pw}@{hostname}/command-api" .format(protocol=protocol, user=username, pw=password, hostname=switch)
        server = jsonrpclib.Server(url)
        try:
        # Try to enable ourselves first
            server.runCmds(1, ["enable"])
        except Exception as e:
            print ("Unable to enable ourselves on this switch", e)
            sys.exit(1)
        apiEndpoints[switch] = server
    return apiEndpoints

def fetchData(switchHostnames, protocol, username, password):
    """ Grab data from the switch """
    endpointData = {}
    for switch in switchHostnames:
        url = "{protocol}://{user}:{pw}@{hostname}/command-api" .format(protocol=protocol, user=username, pw=password, hostname=switch)
        server = jsonrpclib.Server(url)
        try:
            response = server.runCmds(1, ["show hostname"] )
            print ("Hello, my name is: ", response[0][ "hostname" ])
            endpointData[switch] = response[0]["hostname"] # Store hostname data

            try:
                response = server.runCmds(1, ["show version"])
                print ("My MAC address is: ", response[0][ "systemMacAddress" ])
                print ("My Version is: ", response[0][ "version" ])
                endpointData[switch] = response[0]["version"] # Store Version info
                endpointData[switch] = response[0]["systemMacAddress"] # Store Sys MAC

            except jsonrpclib.ProtocolError as e:
                print(f"Protocol error with {switch}: {e}")
            except Exception as e:
                print(f"An error occurred with {switch}: {e}")

            try:
                response = server.runCmds(1, ["show mac address-table count"])

                # Access the vlanCounts data
                vlan_counts = response[0]["vlanCounts"]

                # Print VLAN info
                for vlan_id, counts in vlan_counts.items():
                    dynamic_count = counts.get("dynamic", 0)  # Default to 0 if key doesn't exist
                    unicast_count = counts.get("unicast", 0)  # Default to 0 if it doesn't exist
                    multicast_count = counts.get("multicast", 0)  # Default to 0 is it doesn't exist
                    print(f"VLAN-ID {vlan_id} has {dynamic_count} dynamically learned MAC addresses, {unicast_count} learned unicast addresses and {multicast_count} multicast addresses")

            except jsonrpclib.ProtocolError as e:
                print(f"Protocol error with {switch} (show mac address-table count): {e}")
            except Exception as e:
                print(f"An error occurred with {switch} (show mac address-table count): {e}")

            try:
                response = server.runCmds(1, ["show ip route summary"])

                # Init route_counts variable
                # route_counts = None

                # Is our response structured how we think
                if isinstance(response, list) and len(response) > 0:
                    first_item = response[0]
                    # print(f"First Item: {first_item}")  # Debug line
                    if isinstance(first_item, dict):
                        route_counts = first_item

                        # Access Our Counters
                        connected_count = route_counts.get("connected", 0)
                        static_count = route_counts.get("static", 0)
                        total_count = route_counts.get("totalRoutes", 0)
                        ospf_total_count = route_counts.get("ospfTotal", 0)
                        ospf_intra_area = route_counts.get("ospfIntraArea", 0)  # Intra Area OSPF Routes
                        ospf_inter_area = route_counts.get("ospfInterArea", 0)  #  Inter Area OSPF Routes
                        ospf_external_1 = route_counts.get("ospfExternal1", 0)  #  External Type1 Routes
                        ospf_external_2 = route_counts.get("ospfExternal2", 0)  #  External Type2 Routes
                        ospf_nssa_e1 = route_counts.get("nssaExternal1", 0)  #  NSSA External 1 Type
                        ospf_nssa_e2 = route_counts.get("nssaExternal2", 0)  #  NSSA External 2 Type
                        bgp_total_count = route_counts.get("bgpTotal", 0)  # Total BGP Routes
                        bgp_external_count = route_counts.get("bgpExternal", 0)  # External BGP Route Count
                        bgp_internal_count = route_counts.get("bgpInternal", 0)  # Internal BGP Routes
                        isis_total = route_counts.get("isisTotal", 0)  # ISIS Total Routes
                        isis_level1 = route_counts.get("isisLevel1", 0)  # ISIS Level1 Routes
                        isis_level2 = route_counts.get("isisLevel2", 0)  # ISIS Level2 routes
                        internal_routes = route_counts.get("internal", 0)  # Internal Routes

                        print(f"Switch Route Information\n")
                        print(f"Connected Routes: {connected_count}\nStatic Routes: {static_count}\nInternal Routes: {internal_routes}\n")
                        print(f"OSPF Routes\nIntra Area Routes: {ospf_intra_area}\nInter Area Routes: {ospf_inter_area}\nExternal Type 1's: {ospf_external_1}\nExternal Type 2's: {ospf_external_2}\nNSSA External Type 1's: {ospf_nssa_e1}\nNSSA External Type 2's: {ospf_nssa_e2}\n")
                        print(f"BGP Routes\neBGP Routes: {bgp_external_count}\niBGP Routes: {bgp_internal_count}\nTotal BGP Routes: {bgp_total_count}\n")
                        print(f"ISIS Routes\nLevel1 Routes: {isis_level1}\nLevel2 Routes: {isis_level2}\nTotal ISIS Routes: {isis_total}\n")
                        print(f"Total Routes For This Switch: {total_count}")
                    else:
                        print(f"The first item is not a dicionary.")
                else:
                    print(f"Unexpected response structre {response}")

            except jsonrpclib.ProtocolError as e:
                print(f"Protocol error with {switch} (show ip route summary): {e}")
            except Exception as e:
                print(f"An error has occured with {switch} (show ip route summary): {e}")


        except jsonrpclib.ProtocolError as e:
            print(f"Protocol error with {switch}: {e}")
        except Exception as e:
            print(f"An error occurred with {switch}: {e}")
            sys.exit(1)
    return endpointData

def main():
    parser = argparse.ArgumentParser(description="Grab Information about Arista Switches")
    parser.add_argument("switches", metavar="SWITCH", nargs="+", help="Hostname or IP Address of your switch")
    parser.add_argument("--username", help="Username to connect", default="admin")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--https", help="Use HTTPS instead of HTTP", action="store_const", const="https", default="http")

    args = parser.parse_args()

    apiEndpoints = getEndpoints(args.switches, args.https, args.username, args.password)
    endpointData = fetchData(args.switches, args.https, args.username, args.password)

if __name__ == "__main__":
    main()
