# Diagrama de arquitectura de despliegue
![Consulta el diagrama de instalación completa](../docs/images/deploy2.png)
# Método 1: ejecutar todos los módulos con Docker
Desde la versión `0.8.2`, las imágenes Docker publicadas por este proyecto solo son compatibles con `arquitectura x86`. Si necesitas desplegarlo en una CPU con `arquitectura arm64`, puedes seguir [este tutorial](docker-build.md) para compilar una `imagen arm64` localmente.

## 1. Instalar Docker

Si tu ordenador todavía no tiene Docker instalado, puedes seguir este tutorial: [instalación de Docker](https://www.runoob.com/docker/ubuntu-docker-install.html)

La instalación completa con Docker tiene dos formas. Puedes [usar el script rápido](#script-rapido) (autor [@VanillaNahida](https://github.com/VanillaNahida))
El script descargará automáticamente los archivos y la configuración necesarios, o bien puedes hacer un [despliegue manual](#despliegue-manual) desde cero.


<a id="script-rapido"></a>
### 1.1 Script rápido
El despliegue es sencillo. Puedes consultar [este video](https://www.bilibili.com/video/BV17bbvzHExd/). La versión en texto es la siguiente:
> [!NOTE]  
> Por el momento solo se ha probado el despliegue con un clic en servidores Ubuntu. No se ha probado en otros sistemas y podrían aparecer bugs extraños.

Conéctate al servidor mediante SSH y ejecuta este script con privilegios de root:
```bash
sudo bash -c "$(wget -qO- https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/docker-setup.sh)"
```

El script completará automáticamente estas tareas:
> 1. Instalar Docker
> 2. Configurar los mirrors
> 3. Descargar / extraer las imágenes
> 4. Descargar el archivo del modelo de reconocimiento de voz
> 5. Guiar la configuración del servidor
>

Después de la configuración básica, consulta las [3 cosas más importantes](#ejecutar-el-programa) y [el reinicio de `xiaozhi-esp32-server`](#reiniciar-xiaozhi-esp32-server) que se mencionan más abajo. Cuando completes esas tres configuraciones, ya podrás usarlo.

<a id="despliegue-manual"></a>
### 1.2 Despliegue manual

#### 1.2.1 Crear directorios

Después de la instalación, debes elegir un directorio donde guardar los archivos de configuración del proyecto. Por ejemplo, puedes crear una carpeta llamada `xiaozhi-server`.

Después de crearla, dentro de `xiaozhi-server` tendrás que crear las carpetas `data` y `models`, y dentro de `models` también deberás crear `SenseVoiceSmall`.

La estructura final será esta:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.2.2 Descargar el archivo del modelo de reconocimiento de voz

De forma predeterminada, el proyecto usa el modelo `SenseVoiceSmall` para convertir voz en texto. Como el modelo es grande, debe descargarse por separado. Después de descargarlo, coloca el archivo `model.pt`
dentro del directorio `models/SenseVoiceSmall`.
Puedes elegir cualquiera de estas dos rutas de descarga:

- Opción 1: descargar `SenseVoiceSmall` desde ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Opción 2: descargar `SenseVoiceSmall` desde Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) Código de extracción:
  `qvna`


#### 1.2.3 Descargar archivos de configuración

Necesitas descargar dos archivos de configuración: `docker-compose_all.yaml` y `config_from_api.yaml`. Debes obtenerlos desde el repositorio del proyecto.

##### 1.2.3.1 Descargar `docker-compose_all.yaml`

Abre en el navegador [este enlace](../main/xiaozhi-server/docker-compose_all.yml)。

En la parte derecha de la página encontrarás un botón llamado `RAW`. Junto a él hay un icono de descarga. Haz clic para descargar `docker-compose_all.yml` y guárdalo dentro de tu
`xiaozhi-server`.

O ejecuta directamente `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml` para descargarlo.

Cuando termine la descarga, vuelve a este tutorial y continúa.

##### 1.2.3.2 Descargar `config_from_api.yaml`

Abre en el navegador [este enlace](../main/xiaozhi-server/config_from_api.yaml)。

En la parte derecha de la página encontrarás un botón llamado `RAW`. Junto a él hay un icono de descarga. Haz clic para descargar `config_from_api.yaml`, guárdalo dentro de la carpeta `data` de tu
`xiaozhi-server` y luego renómbralo a `.config.yaml`.

O ejecuta directamente `wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml` para descargarlo y guardarlo.

Después de descargar los archivos de configuración, comprueba que el contenido de `xiaozhi-server` tenga este aspecto:

```
xiaozhi-server
  ├─ docker-compose_all.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

Si la estructura coincide con la anterior, continúa. Si no, revisa de nuevo por si omitiste algún paso.

## 2. Hacer copia de seguridad de los datos

Si anteriormente ya ejecutaste correctamente el panel de control y allí guardaste información importante como claves, copia primero esos datos fuera del panel. Durante la actualización podría sobrescribirse información previa.

## 3. Limpiar imágenes y contenedores de versiones anteriores
A continuación, abre la terminal o línea de comandos, entra en tu carpeta `xiaozhi-server` y ejecuta:

```
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

<a id="ejecutar-el-programa"></a>
## 4. Ejecutar el programa
Ejecuta este comando para arrancar los contenedores de la nueva versión:

```
docker compose -f docker-compose_all.yml up -d
```

Después ejecuta este comando para ver los logs:

```
docker logs -f xiaozhi-esp32-server-web
```

Cuando aparezcan logs de salida, significará que el `智控台` ha arrancado correctamente.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

Ten en cuenta que en este momento solo está funcionando el `智控台`. Si el puerto `8000` de `xiaozhi-esp32-server` muestra errores, no te preocupes todavía.

Ahora debes abrir el `智控台` en el navegador, usando la dirección `http://127.0.0.1:8002`, y registrar el primer usuario. Ese primer usuario será el superadministrador; los usuarios creados después serán usuarios normales. Los usuarios normales solo pueden vincular dispositivos y configurar agentes; el superadministrador puede gestionar modelos, usuarios, parámetros, etc.

A continuación hay tres cosas importantes que debes hacer:

### Primera cosa importante

Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理` y localiza la primera fila de la lista, cuyo código de parámetro es `server.secret`. Copia su valor desde `参数值`.

Conviene explicar qué es `server.secret`: ese `参数值` es muy importante porque permite que nuestro lado `Server` se conecte con `manager-api`. `server.secret` es una clave que se genera aleatoriamente cada vez que despliegas el módulo manager desde cero.

Después de copiar `参数值`, abre el archivo `.config.yaml` dentro del directorio `data` de `xiaozhi-server`. En este momento, tu archivo de configuración debería verse así:

```
manager-api:
  url:  http://127.0.0.1:8002/xiaozhi
  secret: 你的server.secret值
```
1、Pega el valor de `server.secret` que acabas de copiar del `智控台` dentro del campo `secret` del archivo `.config.yaml`.

2、Como estás usando un despliegue con Docker, cambia `url` a `http://xiaozhi-esp32-server-web:8002/xiaozhi`

3、Como estás usando un despliegue con Docker, cambia `url` a `http://xiaozhi-esp32-server-web:8002/xiaozhi`

4、Como estás usando un despliegue con Docker, cambia `url` a `http://xiaozhi-esp32-server-web:8002/xiaozhi`

El resultado debería quedar así:
```
manager-api:
  url: http://xiaozhi-esp32-server-web:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

Después de guardar, continúa con la segunda cosa importante.

### Segunda cosa importante

Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `模型配置` desde el menú superior y luego en `大语言模型` desde la barra lateral izquierda. Busca la primera entrada, `智谱AI`, pulsa `修改`,
y en la ventana emergente pega la clave de `智谱AI` que hayas registrado en el campo `API密钥`. Después guarda.

<a id="reiniciar-xiaozhi-esp32-server"></a>
## 5. Reiniciar xiaozhi-esp32-server

A continuación abre la terminal y ejecuta:
```
docker restart xiaozhi-esp32-server
docker logs -f xiaozhi-esp32-server
```
Si ves logs como estos, significa que Server ha arrancado correctamente:

```
25-02-23 12:01:09[core.websocket_server] - INFO - Websocket地址是      ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
25-02-23 12:01:09[core.websocket_server] - INFO - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Como estás usando un despliegue completo, hay dos interfaces importantes que debes escribir en el ESP32.

Interfaz OTA:
```
http://IP_local_del_host:8002/xiaozhi/ota/
```

Interfaz WebSocket:
```
ws://IP_local_del_host:8000/xiaozhi/v1/
```

### Tercera cosa importante

Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理` y localiza el parámetro `server.websocket`. Introduce tu `interfaz WebSocket`.

Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理` y localiza el parámetro `server.ota`. Introduce tu `interfaz OTA`.

Después de esto ya puedes empezar a trabajar con tu dispositivo ESP32. Puedes `compilar tu propio firmware ESP32` o configurar el uso del `firmware ya compilado por Xia Ge en versión 1.6.1 o superior`. Elige una de estas dos opciones:

1、 [Compilar tu propio firmware ESP32](firmware-build.md)

2、 [Configurar un servidor personalizado a partir del firmware compilado por Xia Ge](firmware-setting.md)


# Método 2: ejecutar todos los módulos desde código fuente local

## 1. Instalar la base de datos MySQL

Si tu máquina ya tiene MySQL instalado, puedes crear directamente una base de datos llamada `xiaozhi_esp32_server`.

```sql
CREATE DATABASE xiaozhi_esp32_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Si todavía no tienes MySQL, puedes instalarlo con Docker:

```
docker run --name xiaozhi-esp32-server-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -e MYSQL_DATABASE=xiaozhi_esp32_server -e MYSQL_INITDB_ARGS="--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci" -e TZ=Asia/Shanghai -d mysql:latest
```

## 2. Instalar Redis

Si todavía no tienes Redis, puedes instalarlo con Docker:

```
docker run --name xiaozhi-esp32-server-redis -d -p 6379:6379 redis
```

## 3. Ejecutar el programa `manager-api`

3.1 Instalar JDK21 y configurar las variables de entorno de JDK

3.2 Instalar Maven y configurar las variables de entorno de Maven

3.3 Usar VS Code e instalar los plugins relacionados con el entorno Java

3.4 Cargar el módulo `manager-api` con VS Code

Configura la conexión a la base de datos dentro de `src/main/resources/application-dev.yml`

```
spring:
  datasource:
    username: root
    password: 123456
```
Configura la conexión a Redis dentro de `src/main/resources/application-dev.yml`
```
spring:
    data:
      redis:
        host: localhost
        port: 6379
        password:
        database: 0
```

3.5 Ejecutar el programa principal

Este proyecto es una aplicación Spring Boot. La forma de arrancarlo es:
abrir `Application.java` y ejecutar el método `Main`

```
Ruta:
src/main/java/xiaozhi/AdminApplication.java
```

Cuando aparezcan logs de salida, significará que `manager-api` se ha iniciado correctamente.

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

## 4. Ejecutar el programa `manager-web`

4.1 Instalar Node.js

4.2 Cargar el módulo `manager-web` con VS Code

Entra desde la terminal en el directorio `manager-web`

```
npm install
```
Y luego arranca con:
```
npm run serve
```

Ten en cuenta que, si la interfaz de tu `manager-api` no está en `http://localhost:8002`, durante el desarrollo deberás modificar
la ruta dentro de `main/manager-web/.env.development`

Cuando el arranque se complete correctamente, abre el `智控台` en el navegador usando la dirección `http://127.0.0.1:8001` y registra el primer usuario. Ese primer usuario será el superadministrador; los usuarios creados después serán usuarios normales. Los usuarios normales solo pueden vincular dispositivos y configurar agentes; el superadministrador puede gestionar modelos, usuarios, parámetros, etc.


Importante: después de registrarte correctamente, inicia sesión en el panel de control con una cuenta de superadministrador, entra en `模型配置` desde el menú superior y luego en `大语言模型` desde la barra lateral izquierda. Busca la primera entrada, `智谱AI`, pulsa `修改`,
y en la ventana emergente pega la clave de `智谱AI` que hayas registrado en el campo `API密钥`. Después guarda.

Importante: después de registrarte correctamente, inicia sesión en el panel de control con una cuenta de superadministrador, entra en `模型配置` desde el menú superior y luego en `大语言模型` desde la barra lateral izquierda. Busca la primera entrada, `智谱AI`, pulsa `修改`,
y en la ventana emergente pega la clave de `智谱AI` que hayas registrado en el campo `API密钥`. Después guarda.

Importante: después de registrarte correctamente, inicia sesión en el panel de control con una cuenta de superadministrador, entra en `模型配置` desde el menú superior y luego en `大语言模型` desde la barra lateral izquierda. Busca la primera entrada, `智谱AI`, pulsa `修改`,
y en la ventana emergente pega la clave de `智谱AI` que hayas registrado en el campo `API密钥`. Después guarda.

## 5. Instalar el entorno Python

Este proyecto usa `conda` para gestionar el entorno de dependencias. Si no te conviene instalar `conda`, tendrás que instalar `libopus` y `ffmpeg` según tu sistema operativo.
Si confirmas que usarás `conda`, después de instalarlo ejecuta los comandos siguientes.

Aviso importante: los usuarios de Windows pueden usar `Anaconda` para gestionar el entorno. Después de instalarlo, busca “anaconda” en el menú Inicio,
encuentra `Anaconda Prompt` y ejecútalo como administrador. Como se muestra en la imagen:

![conda_prompt](./images/conda_env_1.png)

Cuando se abra, si ves un prefijo `(base)` delante de la consola, significa que ya entraste en el entorno `conda`. Entonces podrás ejecutar estos comandos:

![conda_env](./images/conda_env_2.png)

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Añadir los mirrors de Tsinghua
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y

# Si despliegas en Linux y aparece un error por falta de la librería dinámica libiconv.so.2, instálala con:
conda install libiconv -y
```

Ten en cuenta que no basta con lanzar todos los comandos de golpe. Debes ejecutarlos uno por uno y, después de cada paso, revisar los logs para asegurarte de que todo fue bien.

## 6. Instalar las dependencias del proyecto

Primero necesitas descargar el código fuente del proyecto. Puedes hacerlo con `git clone`; si no estás familiarizado con ese comando,

puedes abrir en el navegador esta dirección: `https://github.com/xinnan-tech/xiaozhi-esp32-server.git`

Una vez abierta, busca el botón verde `Code`, ábrelo y verás el botón `Download ZIP`.

Haz clic para descargar el código fuente comprimido. Después de descomprimirlo, es posible que el directorio se llame `xiaozhi-esp32-server-main`.
Debes renombrarlo a `xiaozhi-esp32-server`. Dentro de él entra en la carpeta `main` y luego en `xiaozhi-server`; recuerda bien este directorio `xiaozhi-server`.

```
# Sigue usando el entorno conda
conda activate xiaozhi-esp32-server
# Entra en la raíz del proyecto y luego en main/xiaozhi-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

### 7. Descargar el archivo del modelo de reconocimiento de voz

De forma predeterminada, el proyecto usa el modelo `SenseVoiceSmall` para convertir voz en texto. Como el modelo es grande, debe descargarse por separado. Después de descargarlo, coloca el archivo `model.pt`
dentro del directorio `models/SenseVoiceSmall`.
Puedes elegir cualquiera de estas dos rutas de descarga:

- Opción 1: descargar `SenseVoiceSmall` desde ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Opción 2: descargar `SenseVoiceSmall` desde Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) Código de extracción:
  `qvna`

## 8. Configurar los archivos del proyecto

Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理` y localiza la primera fila de la lista, cuyo código de parámetro es `server.secret`. Copia su valor desde `参数值`.

Conviene explicar qué es `server.secret`: ese `参数值` es muy importante porque permite que nuestro lado `Server` se conecte con `manager-api`. `server.secret` es una clave que se genera aleatoriamente cada vez que despliegas el módulo manager desde cero.

Si dentro de tu directorio `xiaozhi-server` no existe `data`, debes crearlo.
Si dentro de `data` no existe `.config.yaml`, puedes copiar `config_from_api.yaml` desde el directorio `xiaozhi-server` hacia `data` y renombrarlo como `.config.yaml`

Después de copiar `参数值`, abre el archivo `.config.yaml` dentro del directorio `data` de `xiaozhi-server`. En este momento, tu archivo de configuración debería verse así:

```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 你的server.secret值
```

Pega el valor de `server.secret` que acabas de copiar del `智控台` dentro del campo `secret` del archivo `.config.yaml`.

El resultado debería quedar así:
```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

## 9. Ejecutar el proyecto

```
# Asegúrate de ejecutar esto dentro del directorio xiaozhi-server
conda activate xiaozhi-esp32-server
python app.py
```

Si ves logs como los siguientes, significa que el servicio del proyecto se ha iniciado correctamente:

```
25-02-23 12:01:09[core.websocket_server] - INFO - Server is running at ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======上面的地址是websocket协议地址，请勿用浏览器访问=======
25-02-23 12:01:09[core.websocket_server] - INFO - 如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

Como estás usando un despliegue completo, tienes dos interfaces importantes:

Interfaz OTA:
```
http://IP_local_de_tu_ordenador:8002/xiaozhi/ota/
```

Interfaz WebSocket:
```
ws://IP_local_de_tu_ordenador:8000/xiaozhi/v1/
```

Debes escribir obligatoriamente ambas direcciones en el `智控台`, porque afectarán al reparto de la dirección WebSocket y a la función de actualización automática.

1、Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理`, localiza el parámetro `server.websocket` e introduce tu `interfaz WebSocket`.

2、Inicia sesión en el panel de control con una cuenta de superadministrador, entra en `参数管理`, localiza el parámetro `server.ota` e introduce tu `interfaz OTA`.


Después de esto ya puedes empezar a trabajar con tu dispositivo ESP32. Puedes `compilar tu propio firmware ESP32` o configurar el uso del `firmware ya compilado por Xia Ge en versión 1.6.1 o superior`. Elige una de estas dos opciones:

1、 [Compilar tu propio firmware ESP32](firmware-build.md)

2、 [Configurar un servidor personalizado a partir del firmware compilado por Xia Ge](firmware-setting.md)

# Preguntas frecuentes
Estas son algunas preguntas frecuentes como referencia:

1、[¿Por qué Xiaozhi reconoce muchas palabras en coreano, japonés o inglés cuando hablo?](./FAQ.md)<br/>
2、[¿Por qué aparece “TTS 任务出错 文件不存在”?](./FAQ.md)<br/>
3、[TTS falla con frecuencia o agota el tiempo de espera](./FAQ.md)<br/>
4、[Puedo conectarme a mi servidor propio por Wi-Fi, pero no en modo 4G](./FAQ.md)<br/>
5、[¿Cómo mejorar la velocidad de respuesta de Xiaozhi?](./FAQ.md)<br/>
6、[Hablo despacio y Xiaozhi me interrumpe cuando hago pausas](./FAQ.md)<br/>
## Tutoriales relacionados con el despliegue
1、[Cómo descargar automáticamente la última versión del proyecto, compilarla y arrancarla](./dev-ops-integration.md)<br/>
2、[Cómo desplegar la pasarela MQTT y habilitar el protocolo MQTT + UDP](./mqtt-gateway-integration.md)<br/>
3、[Cómo integrar con Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>
## Tutoriales de ampliación
1、[Cómo habilitar el registro por número de teléfono en el panel de control](./ali-sms-integration.md)<br/>
2、[Cómo integrar Home Assistant para control domótico](./homeassistant-integration.md)<br/>
3、[Cómo habilitar el modelo visual para tomar fotos y reconocer objetos](./mcp-vision-integration.md)<br/>
4、[Cómo desplegar un punto de acceso MCP](./mcp-endpoint-enable.md)<br/>
5、[Cómo conectar un punto de acceso MCP](./mcp-endpoint-integration.md)<br/>
6、[Cómo habilitar el reconocimiento por huella de voz](./voiceprint-integration.md)<br/>
7、[Guía de configuración de fuentes para el plugin de noticias](./newsnow_plugin_config.md)<br/>
8、[Guía de uso del plugin del clima](./weather-integration.md)<br/>
## Tutoriales relacionados con clonación de voz y despliegue local de voz
1、[Cómo clonar voces en el panel de control](./huoshan-streamTTS-voice-cloning.md)<br/>
2、[Cómo desplegar e integrar voz local con index-tts](./index-stream-integration.md)<br/>
3、[Cómo desplegar e integrar voz local con fish-speech](./fish-speech-integration.md)<br/>
4、[Cómo desplegar e integrar voz local con PaddleSpeech](./paddlespeech-deploy.md)<br/>
## Tutoriales de pruebas de rendimiento
1、[Guía de pruebas de velocidad de cada componente](./performance_tester.md)<br/>
2、[Resultados de pruebas públicas periódicas](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>
