import paramiko
import mysql.connector
from datetime import datetime


SSH_HOST = ''
SSH_PORT = 22
SSH_USER = ''
SSH_PASS = ''

LOG_FILE_PATH = '/var/log/apache2/error.log'


DB_HOST = 'localhost'
DB_USER = 'utilisateur_db'
DB_PASS = 'mot_de_passe_db'
DB_NAME = 'logs_db'

def get_logs_via_ssh():
    logs = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
        
        stdin, stdout, stderr = ssh.exec_command(f'cat {LOG_FILE_PATH}')
        logs = stdout.readlines()

        ssh.close()
        
    except Exception as e:
        print(f"Erreur lors de la connexion SSH : {e}")
    return logs