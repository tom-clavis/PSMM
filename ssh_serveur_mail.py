import os
import ssh_mysql
import send_mail

# Paramètres de connection

# Identifiant de connection ssh
ssh_user = 'monitor'
ssh_key = '/home/hugo/.ssh/id_rsa'

# ----------------------------------------------------------------------

# Adresse IP du serveur MariaDB
mariadb_host = "192.168.140.103"

remote_port=3306 # Le port de mariadb sur la machine distante
local_port=4000 # On choisir un port sur la machine qui lance le script

# Identifiants de l'utilisateur admin de MariaDB
db_user = 'monitor'
db_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = 'ErrorLog'
db_mariadb = 'ErrorLogMariaDB'
db_ftp = "ErrorLogFTP"
db_web = "ErrorLogWeb"

# ---------------------------------------------------------------------

