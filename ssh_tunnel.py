# Pour que ce script fonctionne, vous devez avoir créé et partagé une clé SSH avec le serveur distant ainsi que défini les variables d'environnement. 

# Pour créer une clé SSH et la partager avec le serveur distant, suivez les étapes suivantes :
# Dans un premier temps, exécutez la commande suivante dans le terminal :
# ssh-keygen

#output :
#Generating public/private rsa key pair.
#Enter file in which to save the key (/home/hugo/.ssh/id_rsa):
#Created directory '/home/hugo/.ssh'.
#Enter passphrase (empty for no passphrase):
#Enter same passphrase again:
#Your identification has been saved in /home/hugo/.ssh/id_rsa
#Your public key has been saved in /home/hugo/.ssh/id_rsa.pub

# N'entrez pas de passphrase pour ne pas avoir à saisir de mot de passe à chaque connexion.
# Vous pouvez choisir un autre emplacement pour enregistrer la clé si vous le souhaitez.

# Ensuite, copiez la clé publique sur le serveur distant avec la commande suivante :
# ssh-copy-id username@ip_de_votre_serveur

# Remplacez username par votre nom d'utilisateur et ip_de_votre_serveur par l'adresse IP de votre serveur.

# Pour exécuter ce script vous devez définir les variables d'environement suivantes :

# - SUDO_PASSWORD : le mot de passe de l'utilisateur administrateur du serveur
# - MYSQL_ROOT_PASSWORD : le mot de passe de l'utilisateur root de MariaDB
# - MYSQL_ADMIN_PASSWORD : le mot de passe de l'utilisateur administrateur de MariaDB

# pour cela, exécutez les commandes suivantes dans le terminal :
# export SUDO_PASSWORD="mot_de_passe_administrateur" >> ~/.bashrc
# export MYSQL_ROOT_PASSWORD="mot_de_passe_root" >> ~/.bashrc
# export MYSQL_ADMIN_PASSWORD="mot_de_passe_administrateur_mariadb" >> ~/.bashrc
# source ~/.bashrc

# Le tunnel SSH est un moyen sécurisé de se connecter à un serveur distant et d'accéder à des ressources distantes.
# Il permet de chiffrer les données échangées entre le client et le serveur, ce qui les rend plus sécurisées.
# Il permet également de contourner les restrictions de pare-feu et de NAT en créant un pont entre le client et le serveur.

from sshtunnel import SSHTunnelForwarder
import paramiko
import mysql.connector
import os

class SSHTunnelManager:
    # Classe pour gérer les tunnels SSH et les connexions SSH
    def __init__(self, ssh_user, ssh_host, ssh_port, ssh_key=None):
        self.ssh_user = ssh_user
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_key = ssh_key
        self.tunnel = None
        self.ssh_client = None
        self.sql_connection = None
        self.sudo_passwd = os.getenv("SUDO_PASSWORD") # Récupérer le mot de passe sudo depuis une variable d'environnement



    # Méthode pour ouvrir un tunnel SSH
    def start_tunnel(self, remote_host, remote_port, local_port):

        # Créer un tunnel SSH
        self.tunnel = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port), # Adresse et port du serveur SSH
            ssh_username = self.ssh_user,
            ssh_pkey = self.ssh_key,
            remote_bind_address = (remote_host, remote_port), # Adresse et port de la ressource distante
            local_bind_address = ('127.0.0.1', local_port) # Adresse et port local pour le tunnel
        )
        # Démarrer le tunnel
        self.tunnel.start()
        print(f"Tunnel SSH ouvert sur le port local {self.tunnel.local_bind_port}")

    # Méthode pour fermer un tunnel SSH
    def stop_tunnel(self):
        if self.tunnel:
            self.tunnel.stop()
            print("Tunnel SSH fermé.")

    # Méthode pour se connecter à un serveur SSH
    def connect_ssh(self):
        # Créer un client SSH
        self.ssh_client = paramiko.SSHClient()

        # Charger les clés hôtes du système
        self.ssh_client.load_system_host_keys()

        # Connexion au serveur
        if self.ssh_key:
            self.ssh_client.connect(
                self.ssh_host,
                port = self.ssh_port,
                username = self.ssh_user,
                key_filename = self.ssh_key # Ajouter automatiquement la clé hôte du serveur depuis le fichier de clé privée
            )
            print(f"Connection SSH à {self.ssh_host} en tant que {self.ssh_user} établie.")
        else:
            print("Clé SSH non fournie.")

    # Méthode pour exécuter une commande shell sur le serveur SSH
    def ssh_command(self, command , sudo=False):
        # Vérifier si le client SSH est connecté
        if self.ssh_client is None:
            raise Exception("SSH client non connecté")
        
        # Vérifier si la commande doit être exécutée avec sudo
        if sudo:
            command = f"sudo -S -p '' {command}" # -S : lire le mot de passe depuis stdin, -p '' : pas de prompt
        
        # Exécuter la commande
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")
            return

        # Envoyer le mot de passe sudo si nécessaire
        if sudo and self.sudo_passwd:
            stdin.write(self.sudo_passwd + "\n")
            stdin.flush()

        # Lire les sorties de la commande
        output = stdout.read().decode("utf-8")
        errors = stderr.read().decode("utf_8")
        if output:
            return output
        if errors:
            print(f"Erreurs éventuelles : {errors}")

        return None


    # Méthode pour exécuter une commande sudo sur le serveur SSH
    def sudo_command(self, command):
        return self.ssh_command(command, sudo=True)

    
    # Méthode pour fermer la connexion SSH
    def close_ssh(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("Connection SSH fermée.")

    # Méthode pour se connecter à une base de données MySQL
    def sql_connect(self, db_user, db_password=os.getenv("MYSQL_ADMIN_PASSWORD"), db_name=None):
        self.sql_connection = mysql.connector.connect(
            host = "127.0.0.1", # Localhost car la connexion se fait via le tunnel SSH
            port = self.tunnel.local_bind_port, # Port local du tunnel SSH
            user = db_user,
            password = db_password,
            database = db_name
        )
        self.cursor = self.sql_connection.cursor()

    # Méthode pour fermer la connexion à la base de données MySQL
    def sql_disconnect(self):
        try:
            if self.sql_connection:
                self.sql_connection.close()
                self.cursor.close()
        except NameError as e:
            print("Pas de connexion SQL ouverte.")
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")

    # Méthode pour exécuter une requête SQL
    def execute_sql(self, query, values=None):
        try:
            if self.sql_connection:
                self.cursor.execute(query, values)
                self.sql_connection.commit()
                print("Requête exécutée avec succès.")
        except Exception as e:
            print("Ouvrez une connection SQL.")
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")

    # Méthode pour récupérer les résultats d'une requête SQL
    def sql_fetch(self, query, values=None):
        try:
            if self.sql_connection:
                self.cursor.execute(query, values)
                result = self.cursor.fetchall()
                return result
        except NameError as e:
            print("Ouvrez une connection SQL.")
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête : {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    ssh_host = '192.168.140.103' # ou "192.168.1.22"
    ssh_port = 22
    ssh_user = "monitor"
    key = "/home/hugo/.ssh/id_rsa"

    remote_host = "127.0.0.1" # Localhost car tunnel SSH
    remote_port = 3306
    local_port = 8080

    db_user = "root"
    db_password = os.getenv("MYSQL_ROOT_PASSWORD")
    db_name = "ErrorLog"

    sshtm = SSHTunnelManager(ssh_user, ssh_host, ssh_port, ssh_key=key)
    sshtm.start_tunnel(remote_host, remote_port, local_port)
    sshtm.connect_ssh()
    liste = sshtm.ssh_command("ls -l")
    print(liste)
    sshtm.sql_connect(db_user, db_password)
    result = sshtm.sql_fetch("SHOW DATABASES;")
    print(result)
    sshtm.sql_disconnect()
    sshtm.close_ssh()
    sshtm.stop_tunnel()