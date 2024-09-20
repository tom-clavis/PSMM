import paramiko

def ssh_login(hostname, username, port, command):
    try:
        # Create a new SSHClient
        client = paramiko.SSHClient()

        # Load the system host keys
        client.load_system_host_keys()

        # Automatically add the server's host key
        key = paramiko.RSAKey.from_private_key_file("/home/hugo/.ssh/id_rsa")

        # Connect to the server
        client.connect(hostname, port, username, pkey=key)
        print(f'Connected to {hostname} as {username}')

        # execute a command shell
        stdin, stdout, stderr = client.exec_command(command)
        stdout_output = stdout.read().decode()
        stderr_output = stderr.read().decode()

        if stdout_output:
            print(stdout_output)
        if stderr_output:
            print(f'STDERR: {stderr_output}')

    except Exception as e:
        print(f'Error: {e}')

    finally:
        client.close()

if __name__ == '__main__':
    hostname = '192.168.140.101'
    username = 'monitor'
    command = 'ls -l'
    port = 22

    # Call the function
    ssh_login(hostname, username, port, command)