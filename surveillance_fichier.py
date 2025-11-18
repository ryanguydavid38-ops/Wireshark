import os
from pathlib import Path
import time

class Surveillance:
  
  def __init__(self, ch_dossier): # ch_dossier est le chemin du dossier à surveiller, qui sera entré par l'utilisateur (pour l'instant)
    self.dossier = Path(ch_dossier) # définit le chemin du dossier sur "dossier"
    self.a_fichiers = set(os.listdir(self.dossier)) # prend les fichiers actuelles dans le dossier du dessus et les listes   


# en construction :

  def scan(self):
    anciens_fichiers = self.a_fichiers # prend la liste des fichiers au début
    nouveaux_fichiers = []
    while True : # BOUCLE INFINIE
      for fich in os.listdir(self.dossier) : #regarde tous les fichiers dans le dossier
        if fich not in anciens_fichiers: # En gros si ca ne trouve pas le fichier, bah il rajoute dans les liste/set
          print(fich)
          nouveaux_fichiers.append(fich) # c'est pour traiter les fichiers en question par un autre programme... faut peut être mettre un return...
          anciens_fichiers.add(fich)  # C'est pour retester la prochaine boucle avec les nouveaux fichiers
      time.sleep(30) #j'ai mis 30 sec pour l'instant
          


# pour tester
test = Surveillance("/home/ubuntu/Documents/LAN/LOG")
print("Le dossier surveillé:")
print(test.dossier)
print("Les fichiers d'origines:")
print(test.a_fichiers)
test.scan()
