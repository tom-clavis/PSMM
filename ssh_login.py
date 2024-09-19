import subprocess

def ssh_command(username, host, port, command):
    try:
        ssh_command = ["ssh", f"{username}@{host}", "-p", str(port), command]

        result = subprocess.run(ssh_command, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Error :")
            print(result.stderr)

    except Exception as e :
        print(f"Error : {e}")

if __name__ == "__main__" :
    username = "monitor"
    host = "192.168.140.101"
    port = 22
    command = "ls -la"

    ssh_command(username, host, port, command)