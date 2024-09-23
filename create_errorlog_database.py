import ssh_tunnel

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

# Identifiant de l'utilisateur administrateur de MariaDB
admin_db = "monitor"

#-----------------------------------------------------------------------------------------------

# Création d'une instance de SSHTunnelManager
tm = ssh_tunnel.SSHTunnelManager(ssh_user, ssh_host, ssh_port, ssh_key)
tm.start_tunnel(mariadb_host, remote_port, local_port)
tm.connect_ssh()

#-----------------------------------------------------------------------------------------------

# Création de la base de données ErrorLog
tm.sql_connect(admin_db)
tm.execute_sql("CREATE DATABASE IF NOT EXISTS ErrorLog;")
print("Base de données 'ErrorLog' créée avec succès.")

#-----------------------------------------------------------------------------------------------

# Création de la table ErrorLogMariaDB
tm.execute_sql("USE ErrorLog;")
tm.execute_sql("""
CREATE TABLE IF NOT EXISTS ErrorLogMariaDB (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(255),
    date DATE,
    heure TIME,
    IP VARCHAR(255)
);
""")
print("Table 'ErrorLogMariaDB' créée avec succès.")

# Création de la table ErrorLogFTP
tm.execute_sql("USE ErrorLog;")
tm.execute_sql("""
CREATE TABLE IF NOT EXISTS ErrorLogFTP (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(255),
    date DATE,
    heure TIME,
    IP VARCHAR(255)
);
""")
print("Table 'ErrorLogFTP' créée avec succès.")

# Création de la table ErrorLogWeb
tm.execute_sql("USE ErrorLog;")
tm.execute_sql("""
CREATE TABLE IF NOT EXISTS ErrorLogWeb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(255),
    date DATE,
    heure TIME,
    IP VARCHAR(255)
);
""")
print("Table 'ErrorLogWeb' créée avec succès.")

tm.execute_sql("USE ErrorLog;")
show_tables = tm.sql_fetch("SHOW TABLES;")
for table in show_tables:
    print(table)

#-----------------------------------------------------------------------------------------------

# Fermeture de la connexion SSH
tm.sql_disconnect()
tm.close_ssh()