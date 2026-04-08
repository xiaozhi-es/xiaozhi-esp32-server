# Método de actualización automática para despliegue completo desde código fuente

Este tutorial está pensado para quienes despliegan todos los módulos desde código fuente y quieren usar comandos automáticos para descargar el código, compilarlo y arrancar los puertos automáticamente, con el fin de conseguir un sistema de actualización lo más eficiente posible.

La plataforma de pruebas de este proyecto, `https://2662r3426b.vicp.fun`, ha usado este método desde su apertura y el resultado ha sido bueno.

También puedes consultar el video del creador de Bilibili `毕乐labs`: [《开源小智服务器xiaozhi-server自动更新以及最新版本MCP接入点配置保姆教程》](https://www.bilibili.com/video/BV15H37zHE7Q)

# Condiciones previas
- Tu ordenador o servidor usa Linux
- Ya has conseguido ejecutar todo el flujo completo
- Te gusta seguir las últimas funciones, pero te resulta molesto hacer el despliegue manual cada vez y quieres un método de actualización automática

La segunda condición es obligatoria, porque algunos archivos y entornos implicados en este tutorial, como JDK, Node.js y Conda, solo existen si ya completaste todo el proceso anteriormente. Si todavía no lo has hecho, puede que no entiendas a qué me refiero cuando mencione ciertos archivos.

# Qué conseguirás con este tutorial
- Resolver el problema de no poder descargar el código fuente más reciente dentro de redes en China continental
- Descargar automáticamente el código y compilar los archivos del frontend
- Descargar automáticamente el código Java, detener el puerto `8002` y volver a arrancarlo
- Descargar automáticamente el código Python, detener el puerto `8000` y volver a arrancarlo

# Paso 1: elegir el directorio del proyecto

Por ejemplo, yo planifiqué este directorio para el proyecto. Es un directorio nuevo y vacío; si quieres evitar errores, puedes usar el mismo:
```
/home/system/xiaozhi
```

# Paso 2: clonar este proyecto
Ahora debes ejecutar primero este comando para descargar el código fuente. Esta dirección sirve para servidores y ordenadores dentro de redes chinas y no requiere VPN.

```
cd /home/system/xiaozhi
git clone https://ghproxy.net/https://github.com/xinnan-tech/xiaozhi-esp32-server.git
```

Después de ejecutarlo, aparecerá una carpeta llamada `xiaozhi-esp32-server` dentro de tu directorio del proyecto. Esa es la fuente del proyecto.

# Paso 3: copiar los archivos base

Si antes ya completaste todo el flujo, te resultarán familiares el archivo de modelo de FunASR `xiaozhi-server/models/SenseVoiceSmall/model.pt` y tu archivo de configuración privado `xiaozhi-server/data/.config.yaml`.

Ahora tienes que copiar `model.pt` al nuevo directorio. Puedes hacerlo así:
```
# Crear los directorios necesarios
mkdir -p /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/

cp 你原来的.config.yaml完整路径 /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml
cp 你原来的model.pt完整路径 /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/models/SenseVoiceSmall/model.pt
```

# Paso 4: crear tres scripts de compilación automática

## 4.1 Compilar automáticamente el módulo `manager-web`
Dentro de `/home/system/xiaozhi/`, crea un archivo llamado `update_8001.sh` con este contenido:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git fetch --all
git reset --hard
git pull origin main


cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web
npm install
npm run build
rm -rf /home/system/xiaozhi/manager-web
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web/dist /home/system/xiaozhi/manager-web
```

Después de guardarlo, ejecuta este comando para darle permisos:
```
chmod 777 update_8001.sh
```
Cuando lo completes, sigue con el siguiente paso.

## 4.2 Compilar y ejecutar automáticamente el módulo `manager-api`
Dentro de `/home/system/xiaozhi/`, crea un archivo llamado `update_8002.sh` con este contenido:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main


cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api
rm -rf target
mvn clean package -Dmaven.test.skip=true
cd /home/system/xiaozhi/

# Buscar el PID que ocupa el puerto 8002
PID=$(sudo netstat -tulnp | grep 8002 | awk '{print $7}' | cut -d'/' -f1)

rm -rf /home/system/xiaozhi/xiaozhi-esp32-api.jar
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api/target/xiaozhi-esp32-api.jar /home/system/xiaozhi/xiaozhi-esp32-api.jar

# Comprobar si se encontró el PID
if [ -z "$PID" ]; then
  echo "没有找到占用8002端口的进程"
else
  echo "找到占用8002端口的进程，进程号为: $PID"
  # Matar el proceso
  kill -9 $PID
  kill -9 $PID
  echo "已杀掉进程 $PID"
fi

nohup java -jar xiaozhi-esp32-api.jar --spring.profiles.active=dev &

tail tail -f nohup.out
```

Después de guardarlo, ejecuta este comando para darle permisos:
```
chmod 777 update_8002.sh
```
Cuando lo completes, sigue con el siguiente paso.

## 4.3 Compilar y ejecutar automáticamente el proyecto Python
Dentro de `/home/system/xiaozhi/`, crea un archivo llamado `update_8000.sh` con este contenido:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

# Buscar el PID que ocupa el puerto 8000
PID=$(sudo netstat -tulnp | grep 8000 | awk '{print $7}' | cut -d'/' -f1)

# Comprobar si se encontró el PID
if [ -z "$PID" ]; then
  echo "没有找到占用8000端口的进程"
else
  echo "找到占用8000端口的进程，进程号为: $PID"
  # Matar el proceso
  kill -9 $PID
  kill -9 $PID
  echo "已杀掉进程 $PID"
fi
cd main/xiaozhi-server
# Inicializar el entorno conda
source ~/.bashrc
conda activate xiaozhi-esp32-server
pip install -r requirements.txt
nohup python app.py >/dev/null &
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

Después de guardarlo, ejecuta este comando para darle permisos:
```
chmod 777 update_8000.sh
```
Cuando lo completes, continúa.

# Actualizaciones diarias

Cuando ya hayas creado todos los scripts anteriores, en las actualizaciones diarias solo tendrás que ejecutar estos comandos en orden para actualizar y arrancar automáticamente:

```
cd /home/system/xiaozhi
# Actualizar y arrancar el programa Java
./update_8001.sh
# Actualizar el programa web
./update_8002.sh
# Actualizar y arrancar el programa Python
./update_8000.sh


# Si más adelante quieres ver los logs de Java, ejecuta:
tail -f nohup.out
# Si más adelante quieres ver los logs de Python, ejecuta:
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

# Notas
La plataforma de pruebas `https://2662r3426b.vicp.fun` usa nginx como proxy inverso. Puedes consultar la configuración detallada de `nginx.conf` [aquí](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)

## Preguntas frecuentes

### 1、¿Por qué no aparece el puerto 8001?
Respuesta: `8001` se usa en el entorno de desarrollo para ejecutar el frontend. Si lo despliegas en un servidor, no se recomienda usar `npm run serve` para arrancar el frontend en el puerto `8001`. En lugar de eso, haz como en este tutorial: compílalo a HTML y deja que nginx gestione el acceso.

### 2、¿Hay que ejecutar manualmente sentencias SQL en cada actualización?
Respuesta: no. El proyecto usa **Liquibase** para gestionar la versión de la base de datos y ejecutará automáticamente los nuevos scripts SQL.
