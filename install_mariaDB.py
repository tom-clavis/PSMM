# Description: This script installs MariaDB on the system.
import os
import subprocess
import command


if __name__ == "__main__":

    Server = "192.168.140.103"

    cnx = command.SSHLogin("monitor", Server)

# install MariaDB
    cnx.sudo_command("apt update -y")
    cnx.sudo_command("apt install mariadb-server -y")
    print("MariaDB installed")

# secure MariaDB
    cnx.sql_root_command("DELETE FROM mysql.user WHERE User='';")
    print("Empty user removed")


    cnx.sql_root_command("DROP DATABASE IF EXISTS test;")
    print("Test database removed")

    utilisateurs_test = cnx.sql_root_command("SELECT User Host FROM mysql.user WHERE Db='test';")
    if utilisateurs_test:
        for utilisateur in utilisateurs_test:
            cnx.sql_root_command(f"REVOKE ALL PRIVILEGES, ON test.* FROM '{utilisateur}';")
    print("Test user removed")

    cnx.sql_root_command("FLUSH PRIVILEGES;")
    print("Privileges flushed")

# restart MariaDB
    cnx.sudo_command("systemctl restart mariadb")
    print("MariaDB restarted")

# create an admin user
    cnx.sql_root_command("CREATE USER 'monitor'@'localhost' IDENTIFIED BY 'monitor';")
    print("Admin user created")

    cnx.sql_root_command("GRANT ALL PRIVILEGES ON *.* TO 'monitor'@'localhost' WITH GRANT OPTION;")
    print("Admin user granted")

    cnx.sql_root_command("UPDATE mysql.user SET Host='localhost' WHERE User = 'root' AND Host != 'localhost';")
    print("Disallow root login remotely")

    cnx.sql_root_command("FLUSH PRIVILEGES;")
    print("Privileges flushed")

    cnx.sql_command("ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';")
    print("MariaDB root password changed")

    print("MariaDB secured")
    print("MariaDB ready to use")