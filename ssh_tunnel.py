from ssh_tunnel import SSHTunnelForwarder
import paramiko
import mysql.connector

class SSHTunnelManager:
    def __init__(self, ssh_user, ssh_host, ssh_port, ssh_password=None, ssh_key=None):
        self.ssh_user = ssh_user
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_password = ssh_password
        self.ssh_key = ssh_key
        self.tunnel = None
        self.ssh_client = None


    def start_tunnel(self, remote_host, remote_port, local_port):
        self.tunnel = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username = self.ssh_user,
            ssh_password = self.ssh_password if self.ssh_password else None,
            ssh_pkey = self.ssh_key if self.ssh_key else None,
            remote_bind_address = ("172.0.0.1", remote_port),
            local_bind_address = ("0.0.0.0", local_port)
        )
        self.tunnel.start()

    def stop_tunnel(self):
        if self.tunnel:
            self.tunnel.stop()
            print("Tunnel SSH fermé.")

    def connection_ssh(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.ssh_password:
            self.ssh_client.connect(
                self.ssh_host,
                port = self.ssh_port,
                username = self.ssh_user,
                password = self.ssh_password
            )
        elif self.ssh_key:
            self.ssh_client.connect(
                self.ssh_host,
                port = self.ssh_port,
                username = self.ssh_user,
                key_filiename = self.ssh_key
            )
        print("Connection SSH établie.")

    def execute_ssh_command(self, command):
        if self.ssh_client is None:
            raise Exception("SSH client non connecté")
        
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8")
        errors = stderr.read().decode("utf_8")

        print(f"Résultat de la commande : {output}")
        if errors:
            print(f"Erreurs éventuelles : {errors}")
    
    def close_ssh(self):
        if self.ssh_client:
            self.ssh_client.close()
            print("Connection SSH fermée.")

    def sql_connect(self, db_user, db_password, db_name):
        self.sql_connection = mysql.connector.connect(
            host = '172.0.0.1',
            port = self.tunnel.local_bind_port,
            user = db_user,
            password = db_password,
            database = db_name
        )
        self.cursor = self.sql_connection.cursor()

    def sql_disconnect(self):
        if self.sql_connection:
            self.sql_connection.close()
            self.cursor.close()

    def execute_sql(self, query, values=None):
        if self.sql_connect:
            self.cursor.execute(query, values)
            self.sql_connection.commit()
            self.sql_disconnect()
        else:
            print("Ouvrez une connection SQL.")

    def sql_fetch(self, query, values=None):
        if self.sql_connection:
            self.cursor.execute(query, values)
            result = self.cursor.fetchall()
            self.sql_disconnect
            return result
        else:
            print("Ouvrez une connectino SQL.")

if __name__ == "__main__":
    ssh_host = "192.168.140.103"
    ssh_port = 22
    ssh_user = "hugo"
    ssh_key = "/home/hugo/.ssh/id-rsa"

    remote_host = "172.0.0.1"
    remote_port = 3306
    local_port = 4000