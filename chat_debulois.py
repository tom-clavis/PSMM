from json import dumps
from httplib2 import Http
import subprocess
import os
import ssh_mysql

def main(message):
    """Google Chat incoming webhook quickstart."""
    url = "https://chat.googleapis.com/v1/spaces/AAAAv4OBpN0/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=R7w7Txc_S4jDnA5iiUoBugYCFxfWiz3Xrkc9P07WESg"
    app_message = {"text": f"{message}"}
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method="POST",
        headers=message_headers,
        body=dumps(app_message),
    )
    print(response)


if __name__ == "__main__":
    # Récupération des logs
    subprocess.run(["python3", "/home/hugo/psmm/ssh_web_error.py"])
    subprocess.run(["python3", "/home/hugo/psmm/ssh_ftp_error.py"])
    subprocess.run(["python3", "/home/hugo/psmm/ssh_mysql_error.py"])

    # Récupération de l'utilisation des serveurs
    subprocess.run(["python3", "/home/hugo/psmm/ssh_system_status.py"])

    # Récupération des données de la base de données
    ssh_host = '192.168.140.103' # Adresse IP de la base de donnée
    ssh_user = 'monitor'
    ssh_key = '/home/hugo/.ssh/id_rsa'
    
    remote_port=3306 # Le port de mariadb sur la machine distante
    local_port=4000 # On choisir un port sur la machine qui lance le script
    
    
    db_user = 'monitor'
    db_password = os.getenv("MYSQL_ADMIN_PASSWORD")
    db_name = 'ErrorLog'


    # Création de l'objet de connexion
    mariadb_tunnel = ssh_mysql.SSHTunnelConnection(ssh_host, ssh_user, ssh_key)
    
    # Démarrer le tunnel SSH
    mariadb_tunnel.tunnel_connect(remote_port, local_port)

    # Création de l'objet de connection a la base de données
    connect=ssh_mysql.MySQL(db_user, db_password, local_port, db_name)

    try:
        logs = [connect.fetch_data(f"SELECT account, date, time, IP FROM ErrorLogMariaDB WHERE id = (SELECT MAX(id) FROM ErrorLogMariaDB);")]
        logs.append(connect.fetch_data(f"SELECT account, date, time, IP FROM ErrorLogFTP WHERE id = (SELECT MAX(id) FROM ErrorLogFTP);"))
        logs.append(connect.fetch_data(f"SELECT account, date, time, IP FROM ErrorLogWeb WHERE id = (SELECT MAX(id) FROM ErrorLogWeb);"))
        message = "Erreurs de connections:\n"
        for log in logs:
            for i in log:
                message += f"compte: {i[0]} Date: {i[1]} heure: {i[2]} IP: {i[3]}\n"


        usage = connect.fetch_data(f"SELECT ip, datetime, cpu, ram, disk FROM Usages ORDER BY id DESC LIMIT 3;")
        message += "Utilisation des serveurs:\n"
        for i in usage:
            message += f"IP: {i[0]} Date: {i[1]} CPU: {i[2]}% RAM: {i[3]}% Disk: {i[4]}%\n"

                
    finally:
        # Fermeture de la connexion
        connect.close_connection()
        mariadb_tunnel.stop_ssh_tunnel()

    main(message)