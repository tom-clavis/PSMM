import mysql.connector
from sshtunnel import SSHTunnelForwarder

class MariaDBSSHConnection:
    def __init__(self, ssh_host, ssh_user, ssh_key, mariadb_host, ssh_port=22):
        # Initialisation du tunnel SSH
        self.server = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=ssh_key,
            remote_bind_address=(mariadb_host, 3306)  # Bind sur l'adresse IP de la machine MariaDB
        )

    def start_ssh_tunnel(self):
        # Démarrer le tunnel SSH
        self.server.start()
        print(f"Tunnel SSH ouvert sur le port local {self.server.local_bind_port}")

    def stop_ssh_tunnel(self):
        # Arrêter le tunnel SSH
        self.server.stop()

    def sql_connect(self, db_user, db_password):
        # Connexion à la base de données via le tunnel SSH
        self.sql_connection = mysql.connector.connect(
            host='127.0.0.1',  # On continue d'utiliser localhost côté client car on passe par le tunnel SSH
            port=self.server.local_bind_port,  # Port local du tunnel SSH
            user=db_user,
            password=db_password
        )
        self.cursor = self.sql_connection.cursor()

    def execute_sql(self, sql_query):
        # Exécution d'une requête SQL
        self.cursor.execute(sql_query)
        self.sql_connection.commit()

    def fetch_data(self, sql_query):
        # Récupération des données d'une requête SQL
        self.cursor.execute(sql_query)
        result = self.cursor.fetchall()
        return result

    def create_database(self, db_name):
        # Création de la base de données
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Base de données '{db_name}' créée avec succès.")

    def close_connection(self):
        # Fermeture des connexions
        if self.sql_connection:
            self.sql_connection.close()
        if self.server:
            self.server.stop()

# Exemple d'utilisation
if __name__ == "__main__":
    ssh_host = '192.168.1.22'
    ssh_user = 'monitor'
    ssh_key = '/home/hugo/.ssh/id_rsa'
    
    mariadb_host = '127.0.0.1'  # Adresse IP de la machine où MariaDB est installé
    db_user = 'monitor'
    db_password = 'root'
    db_name = 'NewDatabase'

    # Création de l'objet de connexion
    mariadb_conn = MariaDBSSHConnection(ssh_host, ssh_user, ssh_key, mariadb_host)
    
    # Démarrer le tunnel SSH
    mariadb_conn.start_ssh_tunnel()

    try:
        # Connexion à MariaDB
        mariadb_conn.sql_connect(db_user, db_password)

        # Créer la base de données
        mariadb_conn.create_database(db_name)

        # Exécuter une requête SQL
        result = mariadb_conn.fetch_data(f"SHOW DATABASES;")
        print(result)
    finally:
        # Fermeture de la connexion
        mariadb_conn.close_connection()
