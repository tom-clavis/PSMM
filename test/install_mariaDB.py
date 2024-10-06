# Description: 
#  - Ce script installe MariaDB sur un serveur distant 
#  - sécurise MariaDB 
#  - crée un utilisateur administrateur.
 
# Suivez les étapes du script ssh_tunntl.py pour définir la clé ssh et les variables d'environnement.

# Ensuite, exécutez le script install_mariaDB.py avec la commande suivante :
# python3 install_mariaDB.py

#-----------------------------------------------------------------------------------------------

import test.ssh_tunnel as ssh_tunnel
import os

# Paramètres de connexion :
# Remplacez les valeurs par les vôtres

# Adresse IP du serveur SSH, port SSH, nom d'utilisateur et clé SSH
ssh_host = "192.168.140.103"
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# Adresse IP du serveur MariaDB, port MariaDB et port local pour le tunnel SSH
mariadb_host = '127.0.0.1'
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur root de MariaDB
root_db = "root"
root_db_password = os.getenv("MSQL_ROOT_PASSWORD")

# Identifiant de l'utilisateur administrateur de MariaDB
admin_db = "monitor"
admin_db_password = os.getenv("MYSQL_ADMIN_PASSWORD")

# -----------------------------------------------------------------------------------------------

# Création d'une instance de SSHTunnelManager
tm = ssh_tunnel.SSHTunnelManager(ssh_user, ssh_host, ssh_port, ssh_key)

# Connexion au serveur MariaDB
tm.start_tunnel(mariadb_host, remote_port, local_port)
tm.connect_ssh()

#-----------------------------------------------------------------------------------------------

# Installation de MariaDB
tm.sudo_command("apt update")
print("fin de l'update")
tm.sudo_command("apt install mariadb-server -y")
print("fin de l'installation de MariaDB")

#-----------------------------------------------------------------------------------------------

#Copie du script de sécurisation de MariaDB : mysql_secure_installation :

#-----------------------------------------------------------------------------------------------

# Changement du mot de passe de l'utilisateur root
tm.sudo_command(f'mariadb -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED BY \'{root_db_password}\';"')
print("Mot de passe de l'utilisateur root changé")

#-----------------------------------------------------------------------------------------------

# Connexion à la base de données en tant que root :
tm.sql_connect(root_db, root_db_password) 
print("Connexion à la base de données réussie")

# Suppression de l'utilisateur anonyme
tm.execute_sql("DELETE FROM mysql.user WHERE User='';")
print("Utilisateur anonyme supprimé")

# Suppression de la base de données de test
tm.execute_sql("DROP DATABASE IF EXISTS test;")
print("Base de données de test supprimée")

# Révocation des privilèges de la base de données de test
users = tm.sql_fetch("SELECT User FROM mysql.user WHERE Db='test';") 
if users:
    for user in users:
        tm.execute_sql(f"REVOKE ALL PRIVILEGES, ON test.* FROM '{user}';")
    print("Privilèges de la base de données de test révoqués")

# Création d'un utilisateur administrateur
tm.execute_sql(f"CREATE USER '{admin_db}'@'localhost' IDENTIFIED BY '{admin_db_password}';")
tm.execute_sql(f"GRANT ALL PRIVILEGES ON *.* TO '{admin_db}'@'localhost' WITH GRANT OPTION;")
print("Utilisateur administrateur créé")
tm.sql_disconnect()

#-----------------------------------------------------------------------------------------------

# Connexion à la base de données en tant que administrateur
tm.sql_connect(admin_db, admin_db_password)

# Blocage de la connexion de root à distance
tm.execute_sql("UPDATE mysql.user SET Host='localhost' WHERE User = 'root' AND Host != 'localhost';")
tm.execute_sql("FLUSH PRIVILEGES;")
print("Connexion de root à distance interdite")

tm.sql_disconnect()

#-----------------------------------------------------------------------------------------------

# Redémarrage de MariaDB
print("Redémarrage de MariaDB")
tm.sudo_command("systemctl restart mariadb")

# Activation du service MariaDB au démarrage
tm.sudo_command("systemctl enable mariadb")
print("MariaDB activé au démarrage")

#-----------------------------------------------------------------------------------------------

# Fermeture de la connexion SSH et du tunnel
tm.close_ssh()
tm.stop_tunnel()

print("MariaDB sécurisé")
print("MariaDB prêt à l'emploi")