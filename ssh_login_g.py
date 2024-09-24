#!usr/bin/python3
import subprocess

commande = ["ssh", "monitor@192.168.140.122", "-p", "22", "mkdir", "new_dossier"]
result = subprocess.run(commande, capture_output=True, text=True)
print(result.stdout)
