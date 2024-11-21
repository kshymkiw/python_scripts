import paramiko
import getpass

def get_user_input():
    """Prompt user for connection information."""
    # Collecting device connection details interactively
    ip_or_fqdn = input("Enter the IP Address or FQDN of the device to connect to: ")
    username = input("Enter the username to connect with: ")
    # Using getpass for securely inputting the password
    password = getpass.getpass("Enter the password for the user: ")
    command = input("Enter the command to send to the device: ")
    
    return ip_or_fqdn, username, password, command

def connect_to_device(ip_or_fqdn, username, password):
    """Establish an SSH connection using Paramiko."""
    try:
        # Create SSH client instance
        ssh_client = paramiko.SSHClient()
        
        # Automatically add the host key (to avoid SSH errors)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {ip_or_fqdn}...")
        ssh_client.connect(ip_or_fqdn, username=username, password=password)
        return ssh_client
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def execute_command(ssh_client, command):
    """Execute a command on the connected device."""
    try:
        print(f"Executing command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Print output and errors
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")
    except Exception as e:
        print(f"Failed to execute command: {e}")

def main():
    # Get user input
    ip_or_fqdn, username, password, command = get_user_input()

    # Establish connection to the device
    ssh_client = connect_to_device(ip_or_fqdn, username, password)
    
    if ssh_client:
        # Execute the command on the device
        execute_command(ssh_client, command)
        
        # Close the connection
        ssh_client.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()

