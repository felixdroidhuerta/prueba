# Makefile para instalar y gestionar el sistema de fichaje por huella

INSTALL_DIR=/opt/fichaje
VENV=$(INSTALL_DIR)/venv
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip

.PHONY: all install venv db run start enable clean

all: install

install: venv db

venv:
	@echo "🔧 Creando entorno virtual y clonando repo en $(INSTALL_DIR)"
	sudo mkdir -p $(INSTALL_DIR)
	sudo chown -R $(USER):$(USER) $(INSTALL_DIR)
	if [ ! -d $(INSTALL_DIR)/.git ]; then git clone https://github.com/felixdroidhuerta/prueba.git $(INSTALL_DIR); fi
	python3 -m venv $(VENV)
	$(PIP) install mysql-connector-python

db:
	sudo systemctl start mysql || true
	sudo mysql -e "CREATE DATABASE IF NOT EXISTS asistencia;"
	sudo mysql -e "CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'Iris.iker1';"
	sudo mysql -e "GRANT ALL PRIVILEGES ON asistencia.* TO 'admin'@'localhost';"
	sudo mysql -e "FLUSH PRIVILEGES;"
	@echo "📚 Inicializando tablas..."
	source $(VENV)/bin/activate && $(PYTHON) - <<'PY'
import sys, os
sys.path.insert(0, os.path.join('$(INSTALL_DIR)', 'src'))
import db; db.init_db()
print('Tablas inicializadas')
PY

run:
	@echo "🚀 Ejecutando la aplicación localmente"
	source $(VENV)/bin/activate && $(PYTHON) $(INSTALL_DIR)/app.py

start:
	sudo systemctl start fichaje

enable:
	sudo systemctl enable fichaje

clean:
	sudo systemctl stop fichaje || true
	sudo systemctl disable fichaje || true
	sudo rm -rf $(INSTALL_DIR)
	sudo rm -f /etc/systemd/system/fichaje.service
	sudo rm -f /etc/logrotate.d/fichaje
	sudo systemctl daemon-reload
