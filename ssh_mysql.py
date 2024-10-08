import mysql.connector
from sshtunnel import SSHTunnelForwarder
import os

class SSHTunnelConnection:
    def __init__(self, ssh_host, ssh_user, ssh_key, ssh_port=22):
        self.ssh_host=ssh_host
        self.ssh_user=ssh_user
        self.ssh_port=ssh_port
        self.ssh_key=ssh_key

    def tunnel_connect(self, remote_port, local_port):
        # Initialisation du tunnel SSH
        self.server = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_pkey=self.ssh_key,
            remote_bind_address=('127.0.0.1', remote_port),
            local_bind_address=('127.0.0.1', local_port)
        )

        self.server.start()
        print(f"Tunnel SSH ouvert sur le port local {self.server.local_bind_port}")

    def stop_ssh_tunnel(self):
        # Arrêter le tunnel SSH
        self.server.stop()

class MySQL:
    def __init__(self, db_user, db_password, local_port, db_name=None, db_table=None):
        self.db_user=db_user
        self.db_password=db_password
        self.db_name=db_name
        self.db_table=db_table
        self.local_port=local_port

        # Connexion à la base de données via le tunnel SSH
        self.sql_connection = mysql.connector.connect(
            host='127.0.0.1',  # On continue d'utiliser localhost côté client car on passe par le tunnel SSH
            port=self.local_port,  # Port local du tunnel SSH
            user=self.db_user,
            password=self.db_password
        )
        self.cursor = self.sql_connection.cursor()

        if db_name:
            self.cursor.execute(f"USE {db_name}")

    def execute_sql(self, sql_query):
        # Exécution d'une requête SQL
        self.cursor.execute(sql_query)
        self.sql_connection.commit()

    def fetch_data(self, sql_query):
        # Récupération des données d'une requête SQL
        self.cursor.execute(sql_query)
        result = self.cursor.fetchall()
        return result

    def insert_logs(self,db_table, username, date, time, ipaddress):
        if self.db_name and db_table:
            self.execute_sql(
                f"INSERT INTO {db_table} (account, date, time, IP) VALUES ('{username}', '{date}', '{time}', '{ipaddress}');"
                )
        else:
            print("Selectionner une base de données et une table")

    def close_connection(self):
        # Fermeture des connexions
        if self.sql_connection:
            self.sql_connection.close()

# Exemple d'utilisation
if __name__ == "__main__":
    ssh_host = '192.168.140.103' # Adresse IP de la base de donnée
    ssh_user = 'monitor'
    ssh_key = '/home/hugo/.ssh/id_rsa'
    
    remote_port=3306 # Le port de mariadb sur la machine distante
    local_port=4000 # On choisir un port sur la machine qui lance le script
    
    
    db_user = 'monitor'
    db_password = os.getenv("MYSQL_ADMIN_PASSWORD")
    db_name = 'ErrorLog'
    db_table = 'ErrorLogMariaDB'

    # Création de l'objet de connexion
    mariadb_tunnel = SSHTunnelConnection(ssh_host, ssh_user, ssh_key)
    
    # Démarrer le tunnel SSH
    mariadb_tunnel.tunnel_connect(remote_port, local_port)

    # Création de l'objet de connection a la base de données
    logMariaDB=MySQL(db_user, db_password, local_port, db_name, db_table)

    try:
        logs=logMariaDB.fetch_data(f"SELECT * FROM ErrorLogMariaDB")
        print(logs)

    finally:
        # Fermeture de la connexion
        logMariaDB.close_connection()
        mariadb_tunnel.stop_ssh_tunnel()
