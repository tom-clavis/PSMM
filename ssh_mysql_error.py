import ssh_mysql
import ssh_login_sudo
import re
import os

# Paramètres de connexion :

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.140.103" # ou 192.168.1.22 selon le réseau
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# Port MariaDB et port local pour le tunnel SSH
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur admin de MariaDB
admin_db = "monitor"
admin_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = "ErrorLog"
db_table = "ErrorLogMariaDB"

# Création d'un client SSH
client = ssh_login_sudo.ssh_connect_sudo(ssh_host, ssh_user, ssh_key, ssh_port)

# Récupération des logs d'erreurs de connection à MariaDB

logs = client.sudo_command("journalctl -u mariadb | grep 'Access denied'")
client.close()

pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(?P<username>\w+)'@'(?P<ipaddress>\w+.\w+.\w+.\w+)'"
data = []
if logs:
    data = re.findall(pattern, logs)
if data:
    # Création d'une instance de SSHTunnelManager
    tm = ssh_mysql.SSHTunnelConnection(ssh_host, ssh_user, ssh_key, ssh_port)

    # Insertion des logs dans la base de données
    tm.tunnel_connect(remote_port, local_port)
    sqlm = ssh_mysql.MySQL(admin_db, admin_password, local_port, db_name, db_table)

    for date, time, username, ipaddress in data:
        check = sqlm.fetch_data(
            f"""SELECT COUNT(*) FROM {db_table} 
            WHERE account = '{username}' 
            AND date = '{date}' 
            AND time = '{time}' 
            AND IP = '{ipaddress}';""")

        if check[0][0] == 0:
            sqlm.insert_logs(db_table, username, date, time, ipaddress)
            print(f"[Insertion] Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

    sqlm.close_connection()
    tm.stop_ssh_tunnel()
print("Fin de la connection")
#-----------------------------------------------------------------------------------------------
