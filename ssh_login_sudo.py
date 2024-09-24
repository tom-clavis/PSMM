# Suivre les étapes de ssh_login.py pour créer une classe SSHLogin qui se connecte à un serveur distant via SSH.

# Pour ce script vous devez avoir défini les variables d'environnement avec la commande export:
# export SUDO_PASSWORD="mot_de_passe_administrateur" >> ~/.bashrc
# source ~/.bashrc

# Pour exécuter ce script vous devez lancer les commandes suivantes dans le terminal :
# python3 ssh_login_sudo.py


import paramiko
import os
from ssh_login import ssh_connect

class ssh_connect_sudo(ssh_connect):
    def __init__(self, hostname, username, pkey, port=22):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.pkey = pkey
        self.sudo_passwd = os.getenv("SUDO_PASSWORD")

        # Créer un nouveau client SSH
        self.ssh_client = paramiko.SSHClient()

        # Charger les clés hôtes du système
        self.ssh_client.load_system_host_keys()

        # Connexion au serveur
        # key_filename : Ajouter automatiquement la clé hôte du serveur depuis le fichier de clé privée
        self.ssh_client.connect(
            self.hostname,
            self.port, 
            self.username, 
            key_filename=self.pkey
            )
        print(f'Connected to {self.hostname} as {self.username}')

    def sudo_command(self, command):
        try:
            # Exécuter une commande shell
            command = f"sudo -S -p '' {command}" # -S : lire le mot de passe depuis stdin, -p '' : pas de prompt
            
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
            except Exception as e:
                print(f"Erreur lors de l'exécution de la commande : {e}")
                return
            stdin.write(self.sudo_passwd + "\n")
            stdin.flush()
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if output:
                return output
            if error:
                print(f'STDERR: {error}')

        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    # Paramètres de connexion
    hostname = '192.168.140.103'
    username = 'monitor'
    pkey = '/home/hugo/.ssh/id_rsa'

    # Appeler la fonction
    ssh = ssh_connect_sudo(hostname, username, pkey)
    ssh.sudo_command('cat /etc/gshadow')
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