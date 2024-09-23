# Suivre les étapes de ssh_login.py pour créer une classe SSHLogin qui se connecte à un serveur distant via SSH.

# Pour ce script vous devez avoir défini les variables d'environnement avec la commande export:
# export SUDO_PASSWORD="mot_de_passe_administrateur"

# Pour exécuter ce script vous devez lancer les commandes suivantes dans le terminal :
# python3 ssh_login_sudo.py


import paramiko
import os
from ssh_login import ssh_connect

class ssh_connect_sudo(ssh_connect):
    def __init__(self, hostname, username, port, pkey):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.pkey = pkey
        self.sudo_passwd = os.getenv("SUDO_PASSWORD")

    def connect(self):
        try:
            # Créer un nouveau client SSH
            self.client = paramiko.SSHClient()

            # Charger les clés hôtes du système
            self.client.load_system_host_keys()

            # Connexion au serveur
            # key_filename : Ajouter automatiquement la clé hôte du serveur depuis le fichier de clé privée
            self.client.connect(
                self.hostname,
                self.port, 
                self.username, 
                key_filename=self.pkey
                )
            print(f'Connected to {self.hostname} as {self.username}')

        except Exception as e:
            print(f'Error: {e}')

    def sudo_command(self, command):
        try:
            # Exécuter une commande shell
            stdin, stdout, stderr = self.client.exec_command(f"echo {self.sudo_passwd} | sudo -S {command}")  
            stdout_output = stdout.read().decode('utf-8')
            stderr_output = stderr.read().decode('utf-8')

            if stdout_output:
                print(stdout_output)
            if stderr_output:
                print(f'STDERR: {stderr_output}')

        except Exception as e:
            print(f'Error: {e}')

    def close(self):
        # Fermer la connexion
        self.client.close()
        print('Connection closed.')

if __name__ == '__main__':
    # Paramètres de connexion
    hostname = '192.168.1.22'
    username = 'monitor'
    command = 'cat /etc/gshadow'
    port = 22
    pkey = '/home/hugo/.ssh/id_rsa'

    # Appeler la fonction
    ssh = ssh_connect_sudo(hostname, username, port, pkey)
    ssh.connect()
    ssh.sudo_command(command)
    ssh.close()

# Output
# Connected to 192.168.1.22 as monitor
# root:*::
# daemon:*::
# bin:*::
# sys:*::
# adm:*::
# ...

# Connection closed.