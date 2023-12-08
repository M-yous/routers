from getpass import getpass
from netmiko import ConnectHandler
from pprint import pprint
import re
import pexpect

username = 'prne'
password = getpass('cisco123!')
secret = 'class123!'

OSPF_pattern = re.compile(r'O.+')
intf_pattern = re.compile(r'(GigabitEthernet)(\d)')

# Create regular expressions to match prefix and routes
prefix_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/?\d?\d?)')
route_pattern = re.compile(r'via (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

session = pexpect.spawn('telnet 192.168.56.101', encoding='utf-8', timeout=20)
result = session.expect(['Username:', pexpect.TIMEOUT, pexpect.EOF])

# Connect to device and run 'show ip route' command
print('--- connecting telnet 192.168.56.101 with prne/cisco123!')




with open('commands_file.txt') as f:
    commands_list = f.read().splitlines()

with open('devices_file.txt') as f:
    devices_list = f.read().splitlines()

for device_ip in devices_list:
    print('Connecting to device: ' + device_ip)
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': device_ip,
        'username': username,
        'password': password,
        'secret': secret,
    }
    net_connect = None # Initialize net_connect to None
    try:
        net_connect = ConnectHandler(**ios_device)
        net_connect.enable()  # Enter privileged exec mode
        output = net_connect.send_config_set(commands_list)
        print(output)

        # Save configuration changes
        output = net_connect.save_config()
        print(output)

    except Exception as e:
        print(f"Failed to connect to {device_ip}. Error: {str(e)}")
#pprint(ConnectHandler)
    finally:
        if net_connect:
        # Disconnect from the device
            net_connect.disconnect()

# Check for failure
if result != 0:
    print('Timeout or unexpected reply from device')
    exit()
# Enter username
session.sendline('prne')
result = session.expect('Password:')

# Enter password
session.sendline('cisco123!')
result = session.expect('>')

# Must set terminal length to zero for long replies, no pauses
print('--- setting terminal length to 0')
session.sendline('terminal length 0')
result = session.expect('>')

# Run the 'show ip route' command on device
print('--- successfully logged into device, running show ip route command')
session.sendline('show ip route')
result = session.expect('>')            

# Display the output of the command, for comparison
print('--- show ip route output:')
show_ip_route_output = session.before
print(show_ip_route_output)


# Get the output from the command into a list of lines from the output
routes_list = show_ip_route_output.splitlines()
# Create dictionary to hold number of routes per interface
intf_routes = {}            

for route in  routes_list:

    OSPF_match = OSPF_pattern.search(route)
    if OSPF_match:

        # Match for GigabitEthernet interfaces
        intf_match = intf_pattern.search(route) 
        
        # Check to see if we matched the GigabitEthernet interfaces string
        if intf_match:

            # Get the interfaces from the match
            intf = intf_match.group(2)

            # If route list not yet created, do so now
            if intf not in intf_routes:
                intf_routes[intf] = []

                # Exract the prefix (destination IP address/subnet)
            prefix_match = prefix_pattern.search(route)
            prefix = prefix_match.group(1)

                # Extract the route
            route_match = route_pattern.search(route)
            next_hop = route_match.group(1)

                # Create dictionary for this this route,
                # and add it to the list
            route = {'prefix': prefix, 'next-hop': next_hop}
            intf_routes[intf].append(route)


# Display a blank line to make easier to read
print('')

# Display a title
print('OSPF routes out of GigabitEthernet interfaces:')

# Display the GigabitEthernet interfaces routes
pprint(intf_routes)

# Display a blank line to make easier to read
print('')
# Close the file
#file.close()            
