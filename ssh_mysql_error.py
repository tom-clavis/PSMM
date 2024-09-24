import ssh_mysql
import ssh_login
import ssh_login_sudo
import re
import os

# Paramètres de connexion :

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.140,103" # ou 192.168.1.22 selon le réseau
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# Adresse IP du serveur MariaDB, port MariaDB et port local pour le tunnel SSH
mariadb_host = '127.0.0.1'
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur admin de MariaDB
admin_db = "monitor"
admin_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = "ErrorLog"
db_table = "ErrorLogMariaDB"

# Création d'une instance de SSHTunnelManager
tm = ssh_mysql.SSHTunnelConnection(ssh_user, ssh_host, ssh_port, ssh_key)

# Création d'un client SSH
client = ssh_login_sudo.ssh_connect_sudo(ssh_host, ssh_user, ssh_key)

# Récupération des logs d'erreurs de connection à MariaDB

logs = client.sudo_command("journalctl -u mariadb | grep 'Access denied'")

pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(?P<username>\w+)'@'(?P<ipaddress>\w+.\w+.\w+.\w+)'"
account = re.findall(pattern, logs)

# Insertion des logs dans la base de données
tm.tunnel_connect(mariadb_host, remote_port, local_port)
sqlm = ssh_mysql.MySQL(admin_db, admin_password, local_port, db_name, db_table)

for date, time, username, ipaddress in account:
    sqlm.execute_sql(f"USE {db_name};")
    sqlm.execute_sql(f"INSERT INTO {db_table} (account, date, heure, IP) VALUES ('{username}', '{date}', '{time}', '{ipaddress}');")
    print(f"Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

sqlm.close_connection()
client.close()
print("Logs insérés avec succès.")
# #-----------------------------------------------------------------------------------------------
