import paramiko
import ssh_login_sudo
import send_mail
import os

reboot_required = []

def update_system(server, user, key_path):
    try:
        client = ssh_login_sudo.ssh_connect_sudo(server, user, key_path)
        update = client.sudo_command("apt update")
        print(f"Mise à jour du système de {server} : {update}")

        if "apt list --upgradable" in update:
            print(f"Téléchargement des paquets de {server}")
            client.sudo_command("apt upgrade -y && apt autoremove -y")
            if client.ssh_command("test -f /var/run/reboot-required"):
                print(f"Redémarrage nécessaire pour {server}")
                reboot_required.append(server)
        client.close()

    except Exception as e:
        print(f"Erreur lors de la connexion à {server} : {e}")
    
if __name__ == '__main__':
    # Paramètres de connexion
    servers = ["192.168.140.101", "192.168.140.102", "192.168.140.103"]
    user = "monitor"
    key_path = "/home/hugo/.ssh/id_rsa"

    for server in servers:
        update_system(server, user, key_path)

    if reboot_required:
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "hugo.esquer@laplateforme.io"
        password = os.getenv('LAPLATEFORME')

        email_sender = send_mail.EmailSender(smtp_server, port, sender_email, password)

        try:
            email_sender.connect()
            
            receiver_email = "esquer.hugo@gmail.com"
            subject = "Reboot required"
            body = "The following servers require a reboot: " + ", ".join(reboot_required)

            email_sender.send_email(receiver_email, subject, body)

        finally:
            email_sender.disconnect()
