#!/bin/sh
# Autor del script: @VanillaNahida
# Este archivo descarga con un solo comando los archivos necesarios del proyecto y crea los directorios automáticamente
# Por ahora solo es compatible con sistemas Ubuntu x86; no se ha probado en otros sistemas

# Define el manejador de interrupciones
handle_interrupt() {
    echo ""
    echo "La instalación fue interrumpida por el usuario (Ctrl+C o Esc)"
    echo "Si necesitas reinstalar, ejecuta el script nuevamente"
    exit 1
}

# Captura la señal para manejar Ctrl+C
trap handle_interrupt SIGINT

# Maneja la tecla Esc
# Guarda la configuración actual del terminal
old_stty_settings=$(stty -g)
# Configura el terminal para responder de inmediato y sin eco
stty -icanon -echo min 1 time 0

# Proceso en segundo plano para detectar la tecla Esc
(while true; do
    read -r key
    if [[ $key == $'\e' ]]; then
        # Se detectó la tecla Esc; dispara la rutina de interrupción
        kill -SIGINT $$
        break
    fi
done) &

# Restaura la configuración del terminal al finalizar el script
trap 'stty "$old_stty_settings"' EXIT


# Imprime el banner en color
echo -e "\e[1;32m"  # Establece color verde brillante
cat << "EOF"
Autor del script: @Bilibili 香草味的纳西妲喵
 __      __            _  _  _            _   _         _      _      _        
 \ \    / /           (_)| || |          | \ | |       | |    (_)    | |       
  \ \  / /__ _  _ __   _ | || |  __ _    |  \| |  __ _ | |__   _   __| |  __ _ 
   \ \/ // _` || '_ \ | || || | / _` |   | . ` | / _` || '_ \ | | / _` | / _` |
    \  /| (_| || | | || || || || (_| |   | |\  || (_| || | | || || (_| || (_| |
     \/  \__,_||_| |_||_||_||_| \__,_|   |_| \_| \__,_||_| |_||_| \__,_| \__,_|                                                                                                                                                                                                                               
EOF
echo -e "\e[0m"  # Restablece el color
echo -e "\e[1;36m  Script de instalación con un clic para el despliegue completo del servidor Xiaozhi Ver 0.2, actualizado el 20 de agosto de 2025 \e[0m\n"
sleep 1



# Comprueba e instala whiptail
check_whiptail() {
    if ! command -v whiptail &> /dev/null; then
        echo "Instalando whiptail..."
        apt update
        apt install -y whiptail
    fi
}

check_whiptail

# Crea el cuadro de confirmación
whiptail --title "Confirmación de instalación" --yesno "Se va a instalar el servidor Xiaozhi. ¿Deseas continuar?" \
  --yes-button "Continuar" --no-button "Salir" 10 50

# Ejecuta según la elección del usuario
case $? in
  0)
    ;;
  1)
    exit 1
    ;;
esac

# Comprueba privilegios de root
if [ $EUID -ne 0 ]; then
    whiptail --title "Error de permisos" --msgbox "Ejecuta este script con privilegios de root" 10 50
    exit 1
fi

# Comprueba la versión del sistema
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" != "debian" ] && [ "$ID" != "ubuntu" ]; then
        whiptail --title "Error del sistema" --msgbox "Este script solo se puede ejecutar en Debian/Ubuntu" 10 60
        exit 1
    fi
else
    whiptail --title "Error del sistema" --msgbox "No se pudo determinar la versión del sistema; este script solo se puede ejecutar en Debian/Ubuntu" 10 60
    exit 1
fi

# Función para descargar archivos de configuración
check_and_download() {
    local filepath=$1
    local url=$2
    if [ ! -f "$filepath" ]; then
        if ! curl -fL --progress-bar "$url" -o "$filepath"; then
            whiptail --title "Error" --msgbox "No se pudo descargar el archivo ${filepath}" 10 50
            exit 1
        fi
    else
        echo "El archivo ${filepath} ya existe; se omite la descarga"
    fi
}

# Comprueba si ya está instalado
check_installed() {
    # Comprueba si el directorio existe y no está vacío
    if [ -d "/opt/xiaozhi-server/" ] && [ "$(ls -A /opt/xiaozhi-server/)" ]; then
        DIR_CHECK=1
    else
        DIR_CHECK=0
    fi
    
    # Comprueba si el contenedor existe
    if docker inspect xiaozhi-esp32-server > /dev/null 2>&1; then
        CONTAINER_CHECK=1
    else
        CONTAINER_CHECK=0
    fi
    
    # Ambas comprobaciones pasaron
    if [ $DIR_CHECK -eq 1 ] && [ $CONTAINER_CHECK -eq 1 ]; then
        return 0  # Instalado
    else
        return 1  # No instalado
    fi
}

# Lógica de actualización
if check_installed; then
    if whiptail --title "Instalación detectada" --yesno "Se detectó una instalación existente del servidor Xiaozhi. ¿Deseas actualizarla?" 10 60; then
        # El usuario eligió actualizar; ejecuta la limpieza
        echo "Iniciando proceso de actualización..."
        
        # Detiene y elimina todos los servicios de docker-compose
        docker compose -f /opt/xiaozhi-server/docker-compose_all.yml down
        
        # Detiene y elimina contenedores concretos (por si alguno no existe)
        containers=(
            "xiaozhi-esp32-server"
            "xiaozhi-esp32-server-web"
            "xiaozhi-esp32-server-db"
            "xiaozhi-esp32-server-redis"
        )
        
        for container in "${containers[@]}"; do
            if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
                docker stop "$container" >/dev/null 2>&1 && \
                docker rm "$container" >/dev/null 2>&1 && \
                echo "Contenedor eliminado correctamente: $container"
            else
                echo "El contenedor no existe; se omite: $container"
            fi
        done
        
        # Elimina imágenes concretas (por si alguna no existe)
        images=(
            "ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest"
            "ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest"
        )
        
        for image in "${images[@]}"; do
            if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${image}$"; then
                docker rmi "$image" >/dev/null 2>&1 && \
                echo "Imagen eliminada correctamente: $image"
            else
                echo "La imagen no existe; se omite: $image"
            fi
        done
        
        echo "Se completaron todas las tareas de limpieza"
        
        # Respalda el archivo de configuración anterior
        mkdir -p /opt/xiaozhi-server/backup/
        if [ -f /opt/xiaozhi-server/data/.config.yaml ]; then
            cp /opt/xiaozhi-server/data/.config.yaml /opt/xiaozhi-server/backup/.config.yaml
            echo "Se respaldó la configuración anterior en /opt/xiaozhi-server/backup/.config.yaml"
        fi
        
        # Descarga la última versión de los archivos de configuración
        check_and_download "/opt/xiaozhi-server/docker-compose_all.yml" "https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml"
        check_and_download "/opt/xiaozhi-server/data/.config.yaml" "https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml"
        
        # Inicia el servicio Docker
        echo "Iniciando los servicios de la versión más reciente..."
        # Marca la actualización como completada para omitir las descargas posteriores
        UPGRADE_COMPLETED=1
        docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d
    else
          whiptail --title "Omitir actualización" --msgbox "La actualización fue cancelada. Se seguirá usando la versión actual." 10 50
          # Omite la actualización y continúa con el flujo posterior
    fi
fi


# Comprueba la instalación de curl
if ! command -v curl &> /dev/null; then
    echo "------------------------------------------------------------"
    echo "No se detectó curl; se va a instalar..."
    apt update
    apt install -y curl
else
    echo "------------------------------------------------------------"
    echo "curl ya está instalado; se omite la instalación"
fi

# Comprueba la instalación de Docker
if ! command -v docker &> /dev/null; then
    echo "------------------------------------------------------------"
    echo "No se detectó Docker; se va a instalar..."
    
    # Usa un mirror nacional en lugar del repositorio oficial
    DISTRO=$(lsb_release -cs)
    MIRROR_URL="https://mirrors.aliyun.com/docker-ce/linux/ubuntu"
    GPG_URL="https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg"
    
    # Instala dependencias básicas
    apt update
    apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg
    
    # Crea el directorio de llaves y añade la llave del mirror nacional
    mkdir -p /etc/apt/keyrings
    curl -fsSL "$GPG_URL" | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Añade el mirror nacional
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] $MIRROR_URL $DISTRO stable" \
        > /etc/apt/sources.list.d/docker.list
    
    # Añade la llave del repositorio oficial como respaldo (por si falla la verificación del mirror nacional)
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 2>/dev/null || \
    echo "Advertencia: no se pudieron añadir algunas llaves; se continuará con la instalación..."
    
    # Instala Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    
    # Inicia el servicio
    systemctl start docker
    systemctl enable docker
    
    # Comprueba si se instaló correctamente
    if docker --version; then
        echo "------------------------------------------------------------"
        echo "¡Docker se instaló correctamente!"
    else
        whiptail --title "Error" --msgbox "La instalación de Docker falló; revisa los logs." 10 50
        exit 1
    fi
else
    echo "Docker ya está instalado; se omite la instalación"
fi

# Configuración del mirror de Docker
MIRROR_OPTIONS=(
    "1" "Mirror XuanYuan (Recomendado)"
    "2" "Mirror de Tencent Cloud"
    "3" "Mirror de USTC"
    "4" "Mirror de NetEase 163"
    "5" "Mirror de Huawei Cloud"
    "6" "Mirror de Alibaba Cloud"
    "7" "Mirror personalizado"
    "8" "Omitir configuración"
)

MIRROR_CHOICE=$(whiptail --title "Seleccionar mirror de Docker" --menu "Selecciona el mirror de Docker que quieres usar" 20 60 10 \
"${MIRROR_OPTIONS[@]}" 3>&1 1>&2 2>&3) || {
    echo "El usuario canceló la selección; saliendo del script"
    exit 1
}

case $MIRROR_CHOICE in
    1) MIRROR_URL="https://docker.xuanyuan.me" ;; 
    2) MIRROR_URL="https://mirror.ccs.tencentyun.com" ;; 
    3) MIRROR_URL="https://docker.mirrors.ustc.edu.cn" ;; 
    4) MIRROR_URL="https://hub-mirror.c.163.com" ;; 
    5) MIRROR_URL="https://05f073ad3c0010ea0f4bc00b7105ec20.mirror.swr.myhuaweicloud.com" ;; 
    6) MIRROR_URL="https://registry.aliyuncs.com" ;; 
    7) MIRROR_URL=$(whiptail --title "Mirror personalizado" --inputbox "Introduce la URL completa del mirror:" 10 60 3>&1 1>&2 2>&3) ;;
    8) MIRROR_URL="" ;; 
esac

if [ -n "$MIRROR_URL" ]; then
    mkdir -p /etc/docker
    if [ -f /etc/docker/daemon.json ]; then
        cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
    fi
    cat > /etc/docker/daemon.json <<EOF
{
    "dns": ["8.8.8.8", "114.114.114.114"],
    "registry-mirrors": ["$MIRROR_URL"]
}
EOF
    whiptail --title "Configuración completada" --msgbox "El mirror se añadió correctamente: $MIRROR_URL\nPulsa Enter para reiniciar Docker y continuar..." 12 60
    echo "------------------------------------------------------------"
    echo "Iniciando el reinicio del servicio Docker..."
    systemctl restart docker.service
fi

# Crea el directorio de instalación
echo "------------------------------------------------------------"
echo "Iniciando la creación del directorio de instalación..."
# Comprueba y crea el directorio de datos
if [ ! -d /opt/xiaozhi-server/data ]; then
    mkdir -p /opt/xiaozhi-server/data
    echo "Se creó el directorio de datos: /opt/xiaozhi-server/data"
else
    echo "El directorio xiaozhi-server/data ya existe; se omite la creación"
fi

# Comprueba y crea el directorio del modelo
if [ ! -d /opt/xiaozhi-server/models/SenseVoiceSmall ]; then
    mkdir -p /opt/xiaozhi-server/models/SenseVoiceSmall
    echo "Se creó el directorio del modelo: /opt/xiaozhi-server/models/SenseVoiceSmall"
else
    echo "El directorio xiaozhi-server/models/SenseVoiceSmall ya existe; se omite la creación"
fi

echo "------------------------------------------------------------"
echo "Iniciando la descarga del modelo de reconocimiento de voz"
# Descarga el archivo del modelo
MODEL_PATH="/opt/xiaozhi-server/models/SenseVoiceSmall/model.pt"
if [ ! -f "$MODEL_PATH" ]; then
    (
    for i in {1..20}; do
        echo $((i*5))
        sleep 0.5
    done
    ) | whiptail --title "Descargando" --gauge "Iniciando la descarga del modelo de reconocimiento de voz..." 10 60 0
    curl -fL --progress-bar https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt -o "$MODEL_PATH" || {
        whiptail --title "Error" --msgbox "No se pudo descargar el archivo model.pt" 10 50
        exit 1
    }
else
    echo "El archivo model.pt ya existe; se omite la descarga"
fi

# Si la actualización no terminó, ejecuta la descarga
if [ -z "$UPGRADE_COMPLETED" ]; then
    check_and_download "/opt/xiaozhi-server/docker-compose_all.yml" "https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml"
    check_and_download "/opt/xiaozhi-server/data/.config.yaml" "https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml"
fi

# Inicia el servicio Docker
(
echo "------------------------------------------------------------"
echo "Descargando las imágenes de Docker..."
echo "Esto puede tardar varios minutos; espera por favor"
docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d

if [ $? -ne 0 ]; then
    whiptail --title "Error" --msgbox "El servicio Docker no pudo iniciarse. Intenta cambiar el mirror y vuelve a ejecutar este script" 10 60
    exit 1
fi

echo "------------------------------------------------------------"
echo "Comprobando el estado de arranque del servicio..."
TIMEOUT=300
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    if [ $((CURRENT_TIME - START_TIME)) -gt $TIMEOUT ]; then
        whiptail --title "Error" --msgbox "Se agotó el tiempo de espera del arranque; no se encontró el contenido de log esperado dentro del tiempo establecido" 10 60
        exit 1
    fi
    
    if docker logs xiaozhi-esp32-server-web 2>&1 | grep -q "Started AdminApplication in"; then
        break
    fi
    sleep 1
done

    echo "¡El servidor se inició correctamente! Finalizando la configuración..."
    echo "Iniciando servicios..."
    docker compose -f /opt/xiaozhi-server/docker-compose_all.yml up -d
    echo "¡Inicio de servicios completado!"
)

# Configuración de la clave

# Obtiene la dirección pública del servidor
PUBLIC_IP=$(hostname -I | awk '{print $1}')
whiptail --title "Configurar la clave del servidor" --msgbox "Usa el navegador para abrir el siguiente enlace, acceder al panel de control y registrar una cuenta: \n\nDirección local: http://127.0.0.1:8002/\nDirección pública: http://$PUBLIC_IP:8002/ (si es un servidor en la nube, abre los puertos 8000 8001 8002 en el grupo de seguridad).\n\nEl primer usuario registrado será el superadministrador; los usuarios registrados después serán usuarios normales. Los usuarios normales solo pueden vincular dispositivos y configurar agentes; el superadministrador puede gestionar modelos, usuarios, parámetros y otras funciones.\n\nCuando termines de registrarte, pulsa Enter para continuar" 18 70
SECRET_KEY=$(whiptail --title "Configurar la clave del servidor" --inputbox "Inicia sesión en el panel de control con una cuenta de superadministrador\nDirección local: http://127.0.0.1:8002/\nDirección pública: http://$PUBLIC_IP:8002/\nEn el menú superior, entra en Diccionario de parámetros (参数字典) → Gestión de parámetros (参数管理) y localiza el código de parámetro: server.secret (服务器密钥)\nCopia ese valor y pégalo en el siguiente campo\n\nIntroduce la clave (déjalo vacío para omitir esta configuración):" 15 60 3>&1 1>&2 2>&3)

if [ -n "$SECRET_KEY" ]; then
    python3 -c "
import sys, yaml; 
config_path = '/opt/xiaozhi-server/data/.config.yaml'; 
with open(config_path, 'r') as f: 
    config = yaml.safe_load(f) or {}; 
config['manager-api'] = {'url': 'http://xiaozhi-esp32-server-web:8002/xiaozhi', 'secret': '$SECRET_KEY'}; 
with open(config_path, 'w') as f: 
    yaml.dump(config, f); 
"
    docker restart xiaozhi-esp32-server
fi

# Obtiene y muestra la información de direcciones
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Corrige el problema de no poder obtener ws desde los logs; se deja como valor fijo
whiptail --title "¡Instalación completada!" --msgbox "\
Direcciones relacionadas del servidor:\n\
Acceso al panel de administración: http://$LOCAL_IP:8002\n\
Dirección OTA: http://$LOCAL_IP:8002/xiaozhi/ota/\n\
Interfaz de análisis visual: http://$LOCAL_IP:8003/mcp/vision/explain\n\
Dirección WebSocket: ws://$LOCAL_IP:8000/xiaozhi/v1/\n\
\n¡Instalación completada! Gracias por usarlo.\nPulsa Enter para salir..." 16 70
