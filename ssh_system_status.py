import os
import ssh_login_sudo
import ssh_mysql
from datetime import datetime, timedelta

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

# ---------------------------------------------------------------------

# Adresse IP du serveur Web
web_host = "192.168.140.102"

# Adresse IP du serveur FTP
ftp_host = "192.168.140.101"

# ---------------------------------------------------------------------

servers = [mariadb_host, web_host, ftp_host]

usages = {}

for server in servers:
    try:
        client = ssh_login_sudo.ssh_connect(server, ssh_user, ssh_key)
        cpu_usage = client.ssh_command("top -bn2 | grep 'Cpu(s)' | awk '{print $2+$4}' | tail -n1")
        ram_usage = client.ssh_command("top -bn2 | grep 'MiB Mem' | awk '{print $8*100/$4}' | tail -n1")
        hd_usage = client.ssh_command("df -h | grep '/dev/sda1' | awk '{print $5}' | sed 's/%//g'")

        usages[server] = {"cpu": cpu_usage, "ram": ram_usage, "hd": hd_usage}

        client.close()

    except Exception as e:
        usages[server] = {"error": str(e)}

tm = ssh_mysql.SSHTunnelConnection(mariadb_host, ssh_user, ssh_key, ssh_port)
tm.tunnel_connect(remote_port, local_port)
sqlm = ssh_mysql.MySQL(admin_db, admin_password, local_port, db_name)

for server, data in usages.items():
    if "error" in data:
        print(f"Erreur pour {server}: {data['error']}")
    else:
        sqlm.execute_sql(
            f"""INSERT INTO Usages (ip, datetime, cpu, ram, disk) VALUES 
            ('{server}', 
            NOW(), 
            '{data["cpu"]}', 
            '{data["ram"]}', 
            '{data["disk"]}'
            );"""
            )
        
limit_date = datetime.now() - timedelta(hours=72)
limit = limit_date.strftime('%Y-%m-%d %H:%M:%S')

sqlm.execute_sql("DELETE FROM Usage WHERE datetime < ?", (limit,))

sqlm.close_connection
tm.stop_ssh_tunnel