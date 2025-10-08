import sys
import os

# Adiciona o diretório atual ao path do Python
INTERP = os.path.expanduser("~/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Adiciona o diretório do projeto
sys.path.insert(0, os.path.dirname(__file__))

# Importa a aplicação Flask
from app import app as application