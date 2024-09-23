# Vous devez avoir créé et partagé une clé SSH avec le serveur distant pour exécuter ce script.
# Pour cela, exécutez la commande suivante dans le terminal :
# ssh-keygen

#output
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

# Pour exécuter ce script vous devez lancer les commandes suivantes dans le terminal :
# python3 ssh_login.py

import paramiko

class ssh_connect:
    def __init__(self, hostname, username, port, pkey):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.pkey = pkey

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

    def command(self, command):
        try:
            # Exécuter une commande shell
            stdin, stdout, stderr = self.client.exec_command(command)
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
    command = 'ls -l'
    port = 22
    pkey = '/home/hugo/.ssh/id_rsa'

    # Appeler la fonction
    ssh = ssh_connect(hostname, username, port, pkey)
    ssh.connect()
    ssh.command(command)
    ssh.close()

# Output
# Connected to 192.168.1.22 as monitor
# total 4
# drwxr-xr-x 2 monitor monitor 4096 sept  18 15:52 nouveau_dossier

# Connection closed.