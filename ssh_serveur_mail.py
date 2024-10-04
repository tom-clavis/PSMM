import os
import ssh_mysql
import send_mail
from datetime import datetime, timedelta

# Fonction pour convertir une liste en tableau HTML
def liste_to_html(table):
    header = ["ID", "Compte", "Date", "Heure", "IP adresse"]
    if not table or table[0] != header:
        table.insert(0, header)

    if table:
        html = "<table border='1'>"
        for line in table:
            html += "<tr>"
            for cell in line:
                tag = "th" if table.index(line) == 0 else "td"
                html += f"<{tag}>{cell}</{tag}>"
            html += "</tr>"
        html += "</table>"
        return html
    else:
        return f"<p>Pas d'érreurs de connection au serveur {table}</p>"

# ---------------------------------------------------------------------

# Paramètres de connection

# Identifiant de connection ssh
ssh_user = 'monitor'
ssh_key = '/home/hugo/.ssh/id_rsa'

# ----------------------------------------------------------------------

# Adresse IP du serveur MariaDB
mariadb_host = "192.168.140.103"

remote_port=3306 # Le port de mariadb sur la machine distante
local_port=4000 # On choisir un port sur la machine qui lance le script

# Identifiants de l'utilisateur admin de MariaDB
db_user = 'monitor'
db_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = 'ErrorLog'
db_mariadb = 'ErrorLogMariaDB'
db_ftp = "ErrorLogFTP"
db_web = "ErrorLogWeb"

# ---------------------------------------------------------------------

tunnel = ssh_mysql.SSHTunnelConnection(mariadb_host, ssh_user, ssh_key)
tunnel.tunnel_connect(remote_port, local_port)

# Connection a la base de données
mysql_mariadb = ssh_mysql.MySQL(db_user, db_password, local_port, db_name)

# Récupération des logs de la base de données
mariadb = mysql_mariadb.fetch_data(f"SELECT * FROM {db_mariadb} WHERE date = CURDATE() - INTERVAL 1 DAY;")
ftp = mysql_mariadb.fetch_data(f"SELECT * FROM {db_ftp} WHERE date = CURDATE() - INTERVAL 1 DAY;")
web = mysql_mariadb.fetch_data(f"SELECT * FROM {db_web} WHERE date = CURDATE() - INTERVAL 1 DAY;")

# Fermeture de la connection
mysql_mariadb.close_connection()
tunnel.stop_ssh_tunnel()

# formatage des logs
logs_mariadb = liste_to_html(mariadb)
logs_ftp = liste_to_html(ftp)
logs_web = liste_to_html(web)

# ---------------------------------------------------------------------

# Envoi des logs par e-mail
smtp_server = "smtp.gmail.com"
port = 587
sender_email = "hugo.esquer@laplateforme.io"
password = os.getenv('LAPLATEFORME')

email_sender = send_mail.EmailSender(smtp_server, port, sender_email, password)

try :
    email_sender.connect()

    # Envoi des logs par e-mail
    receiver_email = "esquer.hugo@gmail.com"
    subject = f"[ERREUR] Logs d'erreurs du {(datetime.now()-timedelta(days=1)).strftime('%d/%m/%Y')}"
    body = f"""
<!DOCTYPE html>
<html>
<body>
    <h1>Logs d'erreurs du {datetime.now().strftime('%d/%m/%Y')}</h1>
    <h2>Logs de connexion MariaDB</h2>
    {logs_mariadb}
    <h2>Logs de connexion FTP</h2>
    {logs_ftp}
    <h2>Logs de connexion Web</h2>
    {logs_web}
</body>
</html>
"""
    email_sender.send_email(receiver_email, subject, body)
    print("[INFO] -> E-mail sent successfully.")
except Exception as e:
    print(f"[ERROR] -> {e}")

finally:
    email_sender.disconnect()
    print("[INFO] -> Disconnected from SMTP server.")