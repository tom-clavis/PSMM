import ssh_login_sudo
import ssh_mysql
import os
import json

# Paramètres de connexion :

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.140.103"
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
# tm = ssh_mysql.SSHTunnelConnection(ssh_user, ssh_host, ssh_port, ssh_key)

# Création d'un client SSH
client = ssh_login_sudo.ssh_connect_sudo(ssh_host, ssh_user, ssh_key)

# Récupération des logs d'erreurs de connection à MariaDB

logs = client.sudo_command("journalctl -u mariadb -o json | grep 'Access denied'")

with open('log_mariadb.log', 'w') as lm:
    lm.write(logs)

client.close()