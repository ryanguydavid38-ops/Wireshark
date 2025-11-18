import os
from pathlib import Path
import time

class surveillance:
  
  def __init__(self, ch_dossier): # ch_dossier est le chemin du dossier à surveiller, qui sera entré par l'utilisateur (pour l'instant)
    self.dossier = Path(ch_dossier) # définit le chemin du dossier sur "dossier"
    self.a_fichiers = set(os.listdir(self.dossier)) # prend les fichiers actuelles dans le dossier du dessus et les listes   


# en construction :

  def scan(self):
    anciens_fichiers = self.a_fichiers
    while True :
      nouveaux_fichiers = []
      for fich in os.listdir(self.dossier) :
        if fich not in anciens_fichiers:
          print(fich)
          nouveaux_fichier.append(fich)
          anciens_fichiers.append(fich)
      time.sleep(30)
          


# pour tester
test = surveillance("/home/ubuntu/Documents/LAN/LOG")
print(test.dossier)
print(test.a_fichiers)

test2 = surveillance
