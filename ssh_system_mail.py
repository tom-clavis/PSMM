import os
import ssh_login_sudo
import time
import send_mail

# Fonction pour convertir une liste en tableau HTML
def liste_to_html(table):

    if table:
        html = "<table border='1'>"
        for line in table:
            html += "<tr>"
            html += f"{line}"
            html += "</tr>"
        html += "</table>"
        return html
    else:
        return f"<p>Pas d'érreurs de connection au serveur {table}</p>"

# ---------------------------------------------------------------------

# Paramètres de connexion :

# identifiant connection ssh
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/hugo/.ssh/id_rsa"

# ---------------------------------------------------------------------

# Adresse IP du serveur MariaDB
mariadb_host = "192.168.140.103"

# Port MariaDB et port local pour le tunnel SSH
remote_port = 3306
local_port = 4000

# Identifiants de l'utilisateur admin de MariaDB
admin_db = "monitor"
admin_password = os.getenv("MYSQL_ADMIN_PASSWORD")
db_name = "ErrorLog"

# ---------------------------------------------------------------------

# Adresse IP du serveur Web
web_host = "192.168.140.102"

# Adresse IP du serveur FTP
ftp_host = "192.168.140.101"

# ---------------------------------------------------------------------

servers = [mariadb_host, web_host, ftp_host]

usages = {}

for server in servers:
    try:
        client = ssh_login_sudo.ssh_connect(server, ssh_user, ssh_key)
        cpu_usage = client.ssh_command("top -bn2 | grep 'Cpu(s)' | awk '{print $2+$4}' | tail -n1")
        ram_usage = client.ssh_command("top -bn2 | grep 'MiB Mem' | awk '{print $8*100/$4}' | tail -n1 | sed 's/..$//'")
        hd_usage = client.ssh_command("df -h | grep '/dev/sda1' | awk '{print $5}' | sed 's/%//g'")

        usages[server] = {"cpu": cpu_usage, "ram": ram_usage, "hd": hd_usage}

        client.close()

    except Exception as e:
        usages[server] = {"error": str(e)}

alertes = []

for server, data in usages.items():
    if "error" in data:
        alertes.append(f"Erreur lors de la connexion à {server} : {data['error']}")
    else:
        cpu = str(data["cpu"]).replace(',', '.')
        ram = str(data["ram"]).replace(',', '.')
        hd = str(data["hd"]).replace(',', '.')
        if float(cpu) > 70:
            alertes.append(f"Alerte : CPU sur {server} ({data['cpu']}%)")
        if float(ram) > 80:
            alertes.append(f"Alerte : RAM sur {server} ({data['ram']}%)")
        if float(hd) > 90:
            alertes.append(f"Alerte : Disque sur {server} ({data['hd']}%)")

if alertes:
    timer = "/tmp/last_mail.lock"

    if os.path.exists(timer):
        last_send = os.path.getmtime(timer)
        now = time.time()
        if (now - last_send) < 3600:
            exit()

    with open(timer, "w") as f:
        f.write("Envoi d'email")

    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "hugo.esquer@laplateforme.io"
    password = os.getenv("LAPLATEFORME")

    email_sender = send_mail.EmailSender(smtp_server, port, sender_email, password)

    alertes_table = liste_to_html(alertes)

    try:
        email_sender.connect()

        receiver_email = "esquer.hugo@gmail.com"
        subject = "Alertes serveurs"
        body = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Alertes serveurs</h1>
            {alertes_table}
        </body>
        </html>
        """
        email_sender.send_email(receiver_email, subject, body)

    finally:
        email_sender.disconnect()