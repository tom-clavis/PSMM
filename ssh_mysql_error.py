import ssh_tunnel
import re

# Paramètres de connexion :

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.1.22"
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# Adresse IP du serveur MariaDB, port MariaDB et port local pour le tunnel SSH
mariadb_host = '127.0.0.1'
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur admin de MariaDB
admin_db = "monitor"
name_db = "ErrorLog"
table_db = "ErrorLogMariaDB"

# Création d'une instance de SSHTunnelManager
tm = ssh_tunnel.SSHTunnelManager(ssh_user, ssh_host, ssh_port, ssh_key)
tm.start_tunnel(mariadb_host, remote_port, local_port)
tm.connect_ssh()

# Récupération des logs d'erreurs de connection à MariaDB

logs = tm.sudo_command("journalctl -u mariadb | grep 'Access denied'")

pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(?P<username>\w+)'@'(?P<ipaddress>\w+.\w+.\w+.\w+)'"
account = re.findall(pattern, logs)

# Insertion des logs dans la base de données
tm.sql_connect(admin_db)

for date, time, username, ipaddress in account:
    tm.execute_sql(f"USE {name_db};")
    tm.execute_sql(f"INSERT INTO {table_db} (account, date, heure, IP) VALUES ('{username}', '{date}', '{time}', '{ipaddress}');")
    print(f"Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

tm.sql_disconnect()
tm.close_ssh()
print("Logs insérés avec succès.")
# #-----------------------------------------------------------------------------------------------
