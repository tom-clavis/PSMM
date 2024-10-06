import test.ssh_tunnel as ssh_tunnel
import re

# Paramètres de connexion :

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.1.22"
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# connect to the server
tm = ssh_tunnel.SSHTunnelManager(ssh_user, ssh_host, ssh_port, ssh_key)
tm.connect_ssh()
logs = tm.sudo_command("journalctl -u mariadb | grep 'Access denied'")

pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(?P<username>\w+)'@'(?P<ipaddress>\w+.\w+.\w+.\w+)'"
account = re.findall(pattern, logs)

for date, time, username, ipaddress in account:
    print(f"Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

tm.close_ssh()

# #-----------------------------------------------------------------------------------------------