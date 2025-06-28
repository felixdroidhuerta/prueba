    #!/bin/bash

    set -e

    echo "🔧 Iniciando configuración automática del sistema de fichaje..."

    # Variables
    INSTALL_DIR="/opt/fichaje"
    DB_USER="admin"
    DB_PASS="Iris.iker1"
    DB_NAME="asistencia"

    echo "📁 Creando directorio de instalación en $INSTALL_DIR"
    sudo mkdir -p $INSTALL_DIR
    sudo chown $USER:$USER $INSTALL_DIR
    cd $INSTALL_DIR

    echo "🔄 Actualizando el sistema y requisitos..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv python3-tk git wget unzip

    echo "🐙 Clonando repositorio..."
    if [ ! -d .git ]; then
        git clone https://github.com/felixdroidhuerta/prueba.git .
    else
        git pull
    fi

    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate

    echo "📦 Instalando dependencias de Python..."
    echo "mysql-connector-python" > requirements.txt
    pip install -r requirements.txt

    echo "🛠️ Instalando MySQL desde repositorio oficial..."
    if ! command -v mysql &> /dev/null; then
        wget -q https://dev.mysql.com/get/mysql-apt-config_0.8.29-1_all.deb
        sudo DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.29-1_all.deb
        sudo apt update
        sudo apt install -y mysql-server
    fi

    echo "🚀 Configurando base de datos MySQL..."
    sudo systemctl start mysql
    sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
    sudo mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';"
    sudo mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
    sudo mysql -e "FLUSH PRIVILEGES;"

    echo "🧠 Ajustando configuración db.py..."
    sed -i "s/'user':.*/'user': '${DB_USER}',/" src/db.py
    sed -i "s/'password':.*/'password': '${DB_PASS}',/" src/db.py
    sed -i "s/'database':.*/'database': '${DB_NAME}'/" src/db.py

    echo "📚 Inicializando tablas (users, records)..."
    source $INSTALL_DIR/venv/bin/activate
    python3 - <<'PY'
import sys, os
sys.path.insert(0, os.path.join("$(pwd)", "src"))
import db
db.init_db()
print("Tablas creadas exitosamente.")
PY

    echo "⚙️ Creando script start.sh..."
    cat <<EOF > start.sh
#!/bin/bash
source $INSTALL_DIR/venv/bin/activate
mkdir -p /var/log/fichaje
python3 $INSTALL_DIR/app.py >> /var/log/fichaje/fichaje.log 2>&1
EOF
    chmod +x start.sh

    echo "⚙️ Creando script setup.sh..."
    cat <<EOF > setup.sh
#!/bin/bash
source $INSTALL_DIR/venv/bin/activate
pip install -r $INSTALL_DIR/requirements.txt
python3 $INSTALL_DIR/app.py
EOF
    chmod +x setup.sh

    echo "🛡️ Configurando servicio systemd..."
    sudo tee /etc/systemd/system/fichaje.service > /dev/null <<EOF
[Unit]
Description=Sistema de Fichaje por Huella
After=network.target mysql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload

    echo "📄 Configurando logrotate..."
    sudo mkdir -p /var/log/fichaje
    sudo chown $USER:$USER /var/log/fichaje

    sudo tee /etc/logrotate.d/fichaje > /dev/null <<EOF
/var/log/fichaje/fichaje.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 root root
    sharedscripts
    postrotate
        systemctl restart fichaje > /dev/null 2>&1 || true
    endscript
}
EOF

    echo "✅ Instalación finalizada. Todo está listo, pero la aplicación NO se ha lanzado automáticamente."
    echo "👉 Puedes arrancarla con: sudo systemctl start fichaje"
