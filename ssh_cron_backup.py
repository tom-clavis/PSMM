import os
import datetime
import glob
from ssh_login_sudo import ssh_connect_sudo

# Récupération des logs dans la base de donées



# -----------------------------------------------------------------------

# Paramètres de connection
mariadb = '192.168.140.103' # Adresse IP du serveur Mariadb
username = 'monitor' # Utilisateur pour la connection SSH
pkey = '/home/hugo/.ssh/id_rsa' # Clé pour la connection SSH

# Paramètre du tunnel SSH
remote_port=3306 # Le port de mariadb sur la machine distante
local_port=4000 # On choisir un port sur la machine qui lance le script

# Identifiant et base de donnée
db_user = 'monitor'
db_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = 'ErrorLog'

# -----------------------------------------------------------------------

# Fichiers de sauvegarde
# Chemin du dossier de sauvegarde
backup_dir = '/home/monitor/backup'

# Nom de fichier avec date
date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = os.path.join(backup_dir, f"{db_name}-{date}.sql")

# -----------------------------------------------------------------------

# Ouvrir la connection SSH
ssh = ssh_connect_sudo(mariadb, username, pkey)

# Créer le dossier de sauvegarde s'il n'existe pas :
# mkdir -p / --parents -> pas  d'erreur  s'il  existe,  
# créer des répertoires parents comme il faut, 
# avec des noms de fichier non touchés par l'option -m.
ssh.ssh_command(f"mkdir -p {backup_dir}") 

# Effectuer la sauvegarde avec myslqdump
try:
    ssh.sudo_command(f'mysqldump -u {db_user} -p"{db_password}" {db_name} > {backup_file}')
except Exception as e:
    print(f"Erreur lors de la sauvegarde: {e}")

# Gestion des sauvegardes
# lister les fichier de sauvegardes
backup_files = sorted(glob.glob(os.path.join(backup_dir, f"{db_name}-*.sql")))
# os.path -> construit le chemin pour trouver les fichiers de sauvegarde
# glob.glob -> trouve tous les fichiers correspondant au motif spécifié
# sorted() -> trie la liste des fichiers trouvé par odre croissant, ici horodatage

if len(backup_files) > 7:
    files_to_delete = backup_files[:-7]
    for file in files_to_delete:
        ssh.ssh_command(f"rm {file}")
        print(f"anciennes sauvegardes supprimé : {file}")

ssh.close()
