import ssh_login_sudo
import ssh_mysql
import os
import re
from datetime import datetime

# Paramètres de connexion :

# identifiant connection ssh
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# ---------------------------------------------------------------------

# Adresse IP du serveur MariaDB
mariadb_host = "192.168.140.103"

# Port MariaDB et port local pour le tunnel SSH
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur admin de MariaDB
admin_db = "monitor"
admin_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = "ErrorLog"
web_table = "ErrorLogWeb"
ftp_table = "ErrorLogFTP"
mariadb_table = "ErrorLogMariaDB"

# ---------------------------------------------------------------------

# Adresse IP du serveur Web
web_host = "192.168.140.102"

# Adresse IP du serveur FTP
ftp_host = "192.168.140.101"

# ---------------------------------------------------------------------

# Récupération des logs de connexion web
# Création d'un client SSH
ftp_client = ssh_login_sudo.ssh_connect_sudo(web_host, ssh_user, ssh_key, ssh_port)

# récupération des log
logs = ftp_client.sudo_command("grep auth_basic:error /var/log/apache2/error.log | sed 's/\]//g' |awk '{print $5, $2, $3, $4, $14, $11}'")
ftp_client.close()
if logs:
    pattern = r"(\d{4} \w{3} \d{2}) (\d{2}:\d{2}:\d{2})\.\d+\s+(\w+)\s+(\d+\.\d+\.\d+.\d+):\d+"
    log_web = re.findall(pattern, logs, re.MULTILINE)
else:
    log_web = []

# Récupération des logs de connexion FTP
# Création d'un client SSH
web_client = ssh_login_sudo.ssh_connect_sudo(ftp_host, ssh_user, ssh_key, ssh_port)

# récupération des log
logs = web_client.sudo_command("cat /var/log/vsftpd.log | grep 'FAIL LOGIN'")
web_client.close()
if logs:
    pattern = r'^(\w{3}\s+\w{3}\s+\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\d{4})\s+\[pid\s+\d+\]\s+\[(\w+)\].*Client\s+"([\d\.]+)"'
    log_ftp = re.findall(pattern, logs, re.MULTILINE)
else:
    log_ftp = []

# Récupération des logs d'erreurs de connection à MariaDB
# Création d'un client SSH
mariadb_client = ssh_login_sudo.ssh_connect_sudo(mariadb_host, ssh_user, ssh_key, ssh_port)

logs = mariadb_client.sudo_command("journalctl -u mariadb | grep 'Access denied'")
mariadb_client.close()
if logs:
    pattern = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(?P<username>\w+)'@'(?P<ipaddress>\w+.\w+.\w+.\w+)'"
    log_mariadb = re.findall(pattern, logs)
else:
    log_mariadb = []

# ---------------------------------------------------------------------

# Création d'une instance de SSHTunnelManager
tm = ssh_mysql.SSHTunnelConnection(mariadb_host, ssh_user, ssh_key, ssh_port)

# Insertion des logs dans la base de données
tm.tunnel_connect(remote_port, local_port)
sqlm = ssh_mysql.MySQL(admin_db, admin_password, local_port, db_name)
sqlm.execute_sql(f"USE {db_name};")

# ---------------------------------------------------------------------

# Insertion des logs de connexion web
for match in log_web:
    date = match[0]
    time = match[1]
    username = match[2]
    ipaddress = match[3]

    date_object = datetime.strptime(date, "%Y %b %d")
    date = datetime.strftime(date_object, "%Y-%m-%d")

    check = sqlm.fetch_data(f"SELECT COUNT(*) FROM {web_table} WHERE account = '{username}' AND date = '{date}' AND time = '{time}' AND IP = '{ipaddress}';")

    if check[0][0] == 0:
        sqlm.insert_logs(web_table, username, date, time, ipaddress)
        print(f"[Insertion table web] Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

# ---------------------------------------------------------------------

# Insertion des logs de connexion FTP
for match in log_ftp:
    date = match[0]     # Date sans l'année
    time = match[1]     # Heure
    year = match[2]     # Année
    username = match[3]     # Nom d'utilisateur
    ipaddress = match[4]       # Adresse IP

    date_str = f"{date} {year}"
    date_object = datetime.strptime(date_str, "%a %b %d %Y")
    date = datetime.strftime(date_object, "%Y-%m-%d")

    check = sqlm.fetch_data(f"SELECT COUNT(*) FROM {ftp_table} WHERE account = '{username}' AND date = '{date}' AND time = '{time}' AND IP = '{ipaddress}';")

    if check[0][0] == 0:
        sqlm.insert_logs(ftp_table, username, date, time, ipaddress)
        print(f"[Insertion table ftp] Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

# ---------------------------------------------------------------------

# Insertion des logs d'erreurs de connection à MariaDB
for date, time, username, ipaddress in log_mariadb:
    check = sqlm.fetch_data(f"SELECT COUNT(*) FROM {mariadb_table} WHERE account = '{username}' AND date = '{date}' AND time = '{time}' AND IP = '{ipaddress}';")

    if check[0][0] == 0:
        sqlm.insert_logs(mariadb_table, username, date, time, ipaddress)
        print(f"[Insertion table Mariadb] Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

# ---------------------------------------------------------------------

# Fermeture de la connection
sqlm.close_connection()
tm.stop_ssh_tunnel()
print("Fin de la connection")
print("Récupération des logs terminée")