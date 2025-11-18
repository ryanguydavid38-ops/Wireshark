import os
from pathlib import Path

class surveillance:
  def __init__(self, ch_dossier):
    self.dossier = Path(ch_dossier)
    self.a_fichiers = set(os.listdir(self.dossier))
    
test = surveillance("/home/ubuntu/Documents/LAN/LOG")
print(test.a_fichier)
