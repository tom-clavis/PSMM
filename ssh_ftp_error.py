import ssh_login_sudo
import ssh_mysql
import re
import os
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
db_table = "ErrorLogFTP"

# ---------------------------------------------------------------------

# Adresse IP du serveur FTP
ftp_host = "192.168.140.101"

# ---------------------------------------------------------------------

# Création d'un client SSH
ftp_client = ssh_login_sudo.ssh_connect_sudo(ftp_host, ssh_user, ssh_key, ssh_port)

# récupération des log
logs = ftp_client.sudo_command("cat /var/log/vsftpd.log | grep 'FAIL LOGIN'")
ftp_client.close()

pattern = r'^(\w{3}\s+\w{3}\s+\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\d{4})\s+\[pid\s+\d+\]\s+\[(\w+)\].*Client\s+"([\d\.]+)"'
data = []
if logs:
    data = re.findall(pattern, logs, re.MULTILINE)

if data:
    # Création d'une instance de SSHTunnelManager
    tm = ssh_mysql.SSHTunnelConnection(mariadb_host, ssh_user, ssh_key, ssh_port)

    # Insertion des logs dans la base de données
    tm.tunnel_connect(remote_port, local_port)
    sqlm = ssh_mysql.MySQL(admin_db, admin_password, local_port, db_name, db_table)
    sqlm.execute_sql(f"USE {db_name};")

    for match in data:
        date = match[0]     # Date sans l'année
        time = match[1]     # Heure
        year = match[2]     # Année
        username = match[3]     # Nom d'utilisateur
        ipaddress = match[4]       # Adresse IP

        date_str = f"{date} {year}"
        date_object = datetime.strptime(date_str, "%a %b %d %Y")
        date = datetime.strftime(date_object, "%Y-%m-%d")

        check = sqlm.fetch_data(f"SELECT COUNT(*) FROM {db_table} WHERE account = '{username}' AND date = '{date}' AND time = '{time}' AND IP = '{ipaddress}';")

        if check[0][0] == 0:
            sqlm.insert_logs(db_table, username, date, time, ipaddress)
            print(f"[Insertion] Date: {date}, Time: {time}, Username: {username}, IP Address: {ipaddress}")

    sqlm.close_connection()
    tm.stop_ssh_tunnel()
print("Fin de la connection")