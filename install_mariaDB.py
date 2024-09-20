# Description: This script installs MariaDB on the system.
import os
import subprocess
import command


if __name__ == "__main__":

    Server = "192.168.140.103"

    cnx = command.SSHLogin("monitor", Server)
    try:
    # install MariaDB
        cnx.sudo_command("apt update -y")
        cnx.sudo_command("apt install mariadb-server -y")
        print("MariaDB installed")
    

    # secure MariaDB
        cnx.sql_sudo_command("DELETE FROM mysql.user WHERE User='';")
        print("Empty user removed")


        cnx.sql_sudo_command("DROP DATABASE IF EXISTS test;")
        print("Test database removed")

        utilisateurs_test = cnx.sql_sudo_command("SELECT User Host FROM mysql.user WHERE Db='test';")
        if utilisateurs_test:
            for utilisateur in utilisateurs_test:
                cnx.sql_sudo_command(f"REVOKE ALL PRIVILEGES, ON test.* FROM '{utilisateur}';")
        print("Test user removed")

        cnx.sql_sudo_command("FLUSH PRIVILEGES;")
        print("Privileges flushed")

    # restart MariaDB
        cnx.sudo_command("systemctl restart mariadb")
        print("MariaDB restarted")

    # create an admin user
        cnx.sql_sudo_command("CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'monitor';")
        print("Admin user created")

        cnx.sql_sudo_command("GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'localhost' WITH GRANT OPTION;")
        print("Admin user granted")

        cnx.sql_sudo_command("ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';")
        print("MariaDB root password changed")

        cnx.sql_command("UPDATE mysql.user SET Host='localhost' WHERE User = 'root' AND Host != 'localhost';")
        print("Disallow root login remotely")

        cnx.sql_sudo_command("FLUSH PRIVILEGES;")
        print("Privileges flushed")

        print("MariaDB secured")
        print("MariaDB ready to use")

    except Exception as e:
        print(f"Error : {e}")
        print("MariaDB installation failed")
        print("MariaDB not ready to use")
        print("Please check the logs")
        print("Exiting")
        exit(1)