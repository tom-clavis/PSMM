import subprocess
import os

class SSHLogin:
    def __init__(self, username, host, port=22):
        self.username = username
        self.host = host
        self.port = port
        self.passwd = os.getenv("SUDO_PASSWD")
        self.ssh_prompt = ["ssh", self.ssh_prompt, "-p", str(self.port)]
        self.sudo_prompt = ["ssh", f"{self.username}@{self.host}", "-p", str(self.port)]



    def ssh_command(self, command):
        try:
            sshCmd = self.ssh_prompt.append(command)

            result = subprocess.run(sshCmd, capture_output=True, text=True)

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("Error :")
                print(result.stderr)

        except Exception as e :
            print(f"Error : {e}")

    def sudo_command(self, command):
        try:
            sudoCmd = self.sudo_prompt.append(f"echo {self.passwd} | sudo -S {command}")

            result = subprocess.run(sudoCmd, capture_output=True, text=True)

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("Error :")
                print(result.stderr)

        except Exception as e :
            print(f"Error : {e}")
    
    def sql_command(self, command):
        try:
            ssh_command = ["ssh", f"{self.username}@{self.host}", "-p", str(self.port), f"echo {self.passwd} | sudo -S {command}"]

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
    ftp = "192.168.140.101"

    cnx_ftp = SSHLogin(username, ftp)

    cnx_ftp.ssh_command("ls -la")
    cnx_ftp.sudo_command("ls -la")