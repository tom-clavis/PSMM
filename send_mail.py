import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self, smtp_server, port, sender_email, password):
        """Initialise le serveur SMTP et les informations d'authentification."""
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.password = password
        self.server = None

    def connect(self):
        """Établit une connexion sécurisée au serveur SMTP."""
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            self.server.starttls()  # Sécuriser la connexion avec TLS
            self.server.login(self.sender_email, self.password)
            print("Connexion au serveur SMTP réussie")
        except Exception as e:
            print(f"Erreur lors de la connexion au serveur SMTP : {e}")
            raise

    def send_email(self, receiver_email, subject, body):
        """Crée et envoie l'e-mail."""
        try:
            # Créer le message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            # Attacher le corps de l'e-mail
            message.attach(MIMEText(body, "html"))

            # Envoyer l'e-mail
            self.server.sendmail(self.sender_email, receiver_email, message.as_string())
            print("E-mail envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail : {e}")
            raise

    def disconnect(self):
        """Ferme la connexion avec le serveur SMTP."""
        if self.server:
            self.server.quit()
            print("Déconnexion du serveur SMTP réussie")

# Utilisation de la classe
if __name__ == "__main__":
    # Informations d'identification
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "hugo.esquer@laplateforme.io"
    password = os.getenv('LAPLATEFORME')

    # Création de l'objet EmailSender
    email_sender = EmailSender(smtp_server, port, sender_email, password)

    # Connexion au serveur SMTP
    try:
        email_sender.connect()

        # Envoi de l'e-mail
        receiver_email = "esquer.hugo@gmail.com"
        subject = "Test script python"
        body = "Ceci est un e-mail envoyé depuis un script Python avec POO."
        email_sender.send_email(receiver_email, subject, body)
    finally:
        # Déconnexion du serveur SMTP
        email_sender.disconnect()
