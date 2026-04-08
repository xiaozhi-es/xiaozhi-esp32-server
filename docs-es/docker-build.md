# Cómo compilar la imagen Docker localmente

Actualmente este proyecto ya usa GitHub para compilar automáticamente las imágenes Docker. Este documento está pensado para quienes necesiten compilarlas de forma local.

1、Instalar Docker
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
2、Compilar la imagen Docker
```
# Entrar en el directorio raíz del proyecto
# Compilar server
docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .
# Compilar web
docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .

# Después de compilar, puedes iniciar el proyecto con docker compose
# Debes cambiar docker-compose.yml para que use la versión de imagen que compilaste
cd main/xiaozhi-server
docker compose up -d
```
