import subprocess
import os

passwd = os.getenv("SUDO_PASSWD")

def sudo_command(username, host, port, command):
    try:
        ssh_command = ["ssh", f"{username}@{host}", "-p", str(port), f"echo {passwd} | sudo -S {command}"]

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

    sudo_command(username, host, port, command)