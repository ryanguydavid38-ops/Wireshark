import os
from pathlib import Path


class surveillance:
  def __init__(self, ch_dossier): # ch_dossier est le chemin du dossier à surveiller, qui sera entré par l'utilisateur (pour l'instant)
    self.dossier = Path(ch_dossier) # définit le chemin du dossier sur "dossier"
    self.a_fichiers = set(os.listdir(self.dossier)) # prend les fichiers actuelles dans le dossier du dessus et les listes

# pour tester, ça fonctionne
test = surveillance("/home/ubuntu/Documents/LAN/LOG")
print(test.dossier)
print(test.a_fichiers)

