# Guía para habilitar el reconocimiento por huella de voz

Este tutorial contiene 3 partes:
- 1、Cómo desplegar el servicio de reconocimiento por huella de voz
- 2、Cómo configurar la interfaz de reconocimiento por huella de voz en un despliegue completo
- 3、Cómo configurar el reconocimiento por huella de voz en un despliegue mínimo

# 1、Cómo desplegar el servicio de reconocimiento por huella de voz

## Paso 1: descargar el código fuente del proyecto de huella de voz

Abre en el navegador la [dirección del proyecto de reconocimiento por huella de voz](https://github.com/xinnan-tech/voiceprint-api)

En la página, busca el botón verde `Code`, ábrelo y verás el botón `Download ZIP`.

Haz clic en él para descargar el código fuente comprimido. Después de descomprimirlo, el directorio puede llamarse `voiceprint-api-main`.
Debes renombrarlo a `voiceprint-api`.

## Paso 2: crear la base de datos y la tabla

El reconocimiento por huella de voz depende de la base de datos `mysql`. Si antes ya desplegaste el `智控台`, eso significa que ya has instalado `mysql` y puedes reutilizarlo.

Puedes probar desde la máquina anfitriona con `telnet` para comprobar si puedes acceder normalmente al puerto `3306` de `mysql`.
```
telnet 127.0.0.1 3306
```
Si puedes acceder al puerto `3306`, ignora el resto de esta sección y pasa directamente al paso 3.

Si no puedes acceder, tendrás que recordar cómo instalaste `mysql`.

Si instalaste `mysql` con un instalador propio, eso significa que tu `mysql` está aislado de la red y probablemente primero tengas que resolver el acceso al puerto `3306`.

Si instalaste `mysql` mediante `docker-compose_all.yml` de este proyecto, tendrás que buscar el archivo `docker-compose_all.yml` que usaste en su momento y modificar lo siguiente:

Antes:
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
```

Después:
```
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
```

La clave está en cambiar `expose` por `ports` bajo `xiaozhi-esp32-server-db`. Después de modificarlo, tendrás que reiniciar. Los comandos para reiniciar MySQL son los siguientes:

```
# Entra en la carpeta donde está tu docker-compose_all.yml; por ejemplo, en mi caso es xiaozhi-server
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

Después del arranque, vuelve a probar desde la máquina anfitriona con `telnet` si puedes acceder normalmente al puerto `3306` de `mysql`.
```
telnet 127.0.0.1 3306
```
En condiciones normales, así ya debería ser accesible.

## Paso 3: crear la base de datos y la tabla
Si tu máquina anfitriona puede acceder normalmente a MySQL, crea en MySQL una base de datos llamada `voiceprint_db` y una tabla `voiceprints`.

```
CREATE DATABASE voiceprint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE voiceprint_db;

CREATE TABLE voiceprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    speaker_id VARCHAR(255) NOT NULL UNIQUE,
    feature_vector LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_speaker_id (speaker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Paso 4: configurar la conexión a la base de datos

Entra en la carpeta `voiceprint-api` y crea un directorio llamado `data`.

Copia `voiceprint.yaml` desde la raíz de `voiceprint-api` a la carpeta `data` y renómbralo como `.voiceprint.yaml`

A continuación, debes configurar especialmente la conexión de base de datos dentro de `.voiceprint.yaml`.

```
mysql:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "your_password"
  database: "voiceprint_db"
```

Atención: como tu servicio de huella de voz está desplegado con Docker, `host` debe contener la IP de red local de la máquina donde está `mysql`.

Atención: como tu servicio de huella de voz está desplegado con Docker, `host` debe contener la IP de red local de la máquina donde está `mysql`.

Atención: como tu servicio de huella de voz está desplegado con Docker, `host` debe contener la IP de red local de la máquina donde está `mysql`.

## Paso 5: iniciar el programa
Este proyecto es bastante simple y se recomienda ejecutarlo con Docker. Si no quieres usar Docker, puedes consultar [esta página](https://github.com/xinnan-tech/voiceprint-api/blob/main/README.md) para ejecutarlo desde el código fuente. A continuación se muestra el método con Docker:

```
# Entrar en el directorio raíz del código fuente del proyecto
cd voiceprint-api

# Limpiar caché
docker compose -f docker-compose.yml down
docker stop voiceprint-api
docker rm voiceprint-api
docker rmi ghcr.nju.edu.cn/xinnan-tech/voiceprint-api:latest

# Iniciar el contenedor Docker
docker compose -f docker-compose.yml up -d
# Ver logs
docker logs -f voiceprint-api
```

En ese momento, los logs mostrarán algo parecido a esto:
```
250711 INFO-🚀 开始: 生产环境服务启动（Uvicorn），监听地址: 0.0.0.0:8005
250711 INFO-============================================================
250711 INFO-声纹接口地址: http://127.0.0.1:8005/voiceprint/health?key=abcd
250711 INFO-============================================================
```

Debes copiar la dirección de la interfaz de huella de voz:

Como estás usando un despliegue con Docker, no debes usar directamente la dirección de arriba.

Como estás usando un despliegue con Docker, no debes usar directamente la dirección de arriba.

Como estás usando un despliegue con Docker, no debes usar directamente la dirección de arriba.

Primero copia esa dirección en un borrador y averigua cuál es la IP de red local de tu ordenador. Por ejemplo, si la IP local de mi ordenador es `192.168.1.25`, entonces
mi dirección original:
```
http://127.0.0.1:8005/voiceprint/health?key=abcd

```
debe cambiarse a:
```
http://192.168.1.25:8005/voiceprint/health?key=abcd
```

Después del cambio, accede directamente desde el navegador a `声纹接口地址`. Si el navegador muestra un código como este, significa que todo ha ido bien:
```
{"total_voiceprints":0,"status":"healthy"}
```

Guarda la `声纹接口地址` ya corregida, porque la necesitarás en el siguiente paso.

# 2、Cómo configurar el reconocimiento por huella de voz en un despliegue completo

## Paso 1: configurar la interfaz
Primero debes habilitar la función de reconocimiento por huella de voz. En el panel de control, haz clic en `参数字典` en la parte superior y luego entra en la página `系统功能配置` desde el menú desplegable. Marca `声纹识别` y pulsa `保存配置`. Entonces verás un botón `声纹识别` en la tarjeta de creación de agentes.

Si usas un despliegue completo, inicia sesión con una cuenta de administrador, haz clic en `参数字典` en la parte superior y entra en `参数管理`.

Luego busca el parámetro `server.voice_print`. En ese momento su valor debería ser `null`.
Haz clic en editar, pega la `声纹接口地址` obtenida en el paso anterior dentro de `参数值` y guarda.

Si el guardado se completa correctamente, todo va bien y ya puedes revisar el efecto en el agente. Si no se guarda, probablemente el panel de control no puede acceder al servicio de huella de voz, casi seguro por un firewall de red o porque no has rellenado bien la IP de red local.

## Paso 2: configurar el modo de memoria del agente

En la configuración de rol de tu agente, establece la memoria en `本地短期记忆` y asegúrate de habilitar `上报文字+语音`.

## Paso 3: hablar con tu agente

Enciende tu dispositivo y habla con él usando una velocidad y una entonación normales.

## Paso 4: registrar la huella de voz

En el panel de control, en la página `智能体管理`, verás un botón `声纹识别` dentro del panel del agente. Haz clic en él. En la parte inferior hay un botón `新增`. Desde ahí puedes registrar la huella de voz de lo que diga una persona concreta.
En la ventana emergente, se recomienda rellenar el campo `描述`; puede ser la profesión, personalidad o aficiones de esa persona. Así el agente podrá analizar y entender mejor a quien habla.

## Paso 3: volver a hablar con tu agente

Enciende tu dispositivo y pregúntale: “¿Sabes quién soy?”. Si puede responder correctamente, entonces la función de reconocimiento por huella de voz está funcionando.

# 3、Cómo configurar el reconocimiento por huella de voz en el despliegue mínimo

## Paso 1: configurar la interfaz
Abre el archivo `xiaozhi-server/data/.config.yaml` (si no existe, créalo) y añade o modifica el contenido siguiente:

```
# Configuración del reconocimiento por huella de voz
voiceprint:
  # Dirección de la interfaz de huella de voz
  url: 你的声纹接口地址
  # Configuración del hablante: speaker_id,nombre,descripción
  speakers:
    - "test1,张三,张三是一个程序员"
    - "test2,李四,李四是一个产品经理"
    - "test3,王五,王五是一个设计师"
```

Pega en `url` la `声纹接口地址` obtenida en el paso anterior y guarda.

El parámetro `speakers` se añade según tus necesidades. Aquí debes prestar atención al parámetro `speaker_id`, porque se utilizará más adelante durante el registro de la huella de voz.

## Paso 2: registrar la huella de voz
Si ya has iniciado el servicio de huella de voz, puedes abrir `http://localhost:8005/voiceprint/docs` en tu navegador local para consultar la documentación de la API. Aquí solo se explica cómo usar la API de registro de huella de voz.

La dirección de la API de registro es `http://localhost:8005/voiceprint/register` y el método de solicitud es `POST`.

La cabecera debe incluir autenticación Bearer Token. El token es la parte posterior a `?key=` dentro de la `声纹接口地址`. Por ejemplo, si mi dirección es `http://127.0.0.1:8005/voiceprint/health?key=abcd`, entonces mi token es `abcd`.

El cuerpo de la petición debe incluir el ID del hablante (`speaker_id`) y el archivo de audio WAV (`file`). Un ejemplo de petición sería:

```
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "speaker_id=your_speaker_id_here" \
  -F "file=@/path/to/your/file" \
  http://localhost:8005/voiceprint/register
```

Aquí `file` es el archivo de audio con la voz de la persona que vas a registrar, y `speaker_id` debe coincidir con el `speaker_id` definido en el primer paso. Por ejemplo, si quiero registrar la huella de voz de 张三 y en `.config.yaml` el `speaker_id` de 张三 es `test1`, entonces al registrar la huella de 张三 el `speaker_id` de la petición debe ser `test1`, y `file` debe ser el archivo de audio con un fragmento de voz de 张三.

 ## Paso 3: iniciar los servicios

Inicia el servidor Xiaozhi y el servicio de huella de voz, y ya podrás usarlo normalmente.
