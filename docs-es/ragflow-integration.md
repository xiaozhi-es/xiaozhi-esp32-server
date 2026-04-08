# Guía de integración de RAGFlow

Este tutorial tiene dos partes principales:

- 1. Cómo desplegar RAGFlow
- 2. Cómo configurar la interfaz de RAGFlow en el panel de control

Si ya conoces bien RAGFlow y ya lo tienes desplegado, puedes saltarte directamente la primera parte y pasar a la segunda. Pero si quieres una guía para desplegar RAGFlow compartiendo los servicios básicos `mysql` y `redis` con `xiaozhi-esp32-server` para reducir costes de recursos, entonces debes empezar desde la primera parte.

# Primera parte: cómo desplegar RAGFlow
## Paso 1: confirmar que MySQL y Redis están disponibles

RAGFlow depende de la base de datos `mysql`. Si ya desplegaste el `智控台`, eso significa que ya has instalado `mysql`. Puedes reutilizarlo.

Puedes probar desde la máquina anfitriona con `telnet` para ver si puedes acceder normalmente a los puertos `3306` de `mysql` y `6379` de `redis`.
``` shell
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```
Si puedes acceder a los puertos `3306` y `6379`, puedes ignorar el resto de esta sección y pasar directamente al paso 2.

Si no puedes acceder, tendrás que recordar cómo instalaste `mysql`.

Si instalaste `mysql` con un instalador propio, eso significa que tu `mysql` está aislado de la red y probablemente primero tengas que resolver el acceso al puerto `3306`.

Si instalaste `mysql` mediante `docker-compose_all.yml` de este proyecto, tendrás que buscar el archivo `docker-compose_all.yml` que usaste en su momento y modificar lo siguiente:

Antes de modificar:
``` yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    expose:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    expose:
      - 6379
```

Después de modificar:
``` yaml
  xiaozhi-esp32-server-db:
    ...
    networks:
      - default
    ports:
      - "3306:3306"
  xiaozhi-esp32-server-redis:
    ...
    ports:
      - "6379:6379"
```

La clave está en cambiar `expose` por `ports` bajo `xiaozhi-esp32-server-db` y `xiaozhi-esp32-server-redis`. Después de modificarlo, tendrás que reiniciar. Los comandos para reiniciar MySQL son los siguientes:

``` shell
# Entra en la carpeta donde está tu docker-compose_all.yml; por ejemplo, en mi caso es xiaozhi-server
cd xiaozhi-server
docker compose -f docker-compose_all.yml down
docker compose -f docker-compose.yml up -d
```

Después del arranque, vuelve a probar desde la máquina anfitriona con `telnet` si puedes acceder normalmente al puerto `3306` de `mysql` y al `6379` de `redis`.
``` shell
telnet 127.0.0.1 3306

telnet 127.0.0.1 6379
```
Normalmente, así ya debería ser accesible.

## Paso 2: crear la base de datos y el usuario
Si tu máquina anfitriona puede acceder normalmente a MySQL, crea en MySQL una base de datos llamada `rag_flow` y un usuario `rag_flow` con contraseña `infini_rag_flow`.

``` sql
-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear el usuario y conceder permisos
CREATE USER IF NOT EXISTS 'rag_flow'@'%' IDENTIFIED BY 'infini_rag_flow';
GRANT ALL PRIVILEGES ON rag_flow.* TO 'rag_flow'@'%';

-- Actualizar privilegios
FLUSH PRIVILEGES;
```

## Paso 3: descargar el proyecto RAGFlow

Necesitas elegir en tu ordenador una carpeta donde guardar el proyecto RAGFlow. Por ejemplo, en mi caso uso `/home/system/xiaozhi`.

Puedes usar `git` para descargar el proyecto RAGFlow en esa carpeta. Este tutorial usa la versión `v0.22.0` para la instalación.
```
git clone https://ghfast.top/https://github.com/infiniflow/ragflow.git
cd ragflow
git checkout v0.22.0
```
Después de descargarlo, entra en la carpeta `docker`.
``` shell
cd docker
```
Modifica el archivo `ragflow/docker/docker-compose.yml` y elimina la configuración `depends_on` de los servicios `ragflow-cpu` y `ragflow-gpu`, para quitar la dependencia de `ragflow-cpu` respecto a `mysql`.

Antes:
``` yaml
  ragflow-cpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - cpu
  ...
  ragflow-gpu:
    depends_on:
      mysql:
        condition: service_healthy
    profiles:
      - gpu
```
Después:
``` yaml
  ragflow-cpu:
    profiles:
      - cpu
  ...
  ragflow-gpu:
    profiles:
      - gpu
```

Luego modifica `ragflow/docker/docker-compose-base.yml` y elimina la configuración de `mysql` y `redis`.

Por ejemplo, antes de eliminar:
``` yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
  mysql:
    image: mysql:8.0
    ...
  redis:
    image: redis:6.2-alpine
    ...
```

Después de eliminar:
``` yaml
services:
  minio:
    image: quay.io/minio/minio:RELEASE.2025-06-13T11-33-47Z
    ...
```
## Paso 4: modificar la configuración de variables de entorno

Edita el archivo `.env` dentro de `ragflow/docker` y localiza las siguientes configuraciones. Búscalas una por una y modifícalas una por una.

Al modificar el archivo `.env`, el 60% de la gente olvida la configuración `MYSQL_USER`, lo que hace que RAGFlow no arranque correctamente. Por eso conviene repetirlo tres veces:

Primera advertencia: si tu archivo `.env` no tiene la configuración `MYSQL_USER`, añádela.

Segunda advertencia: si tu archivo `.env` no tiene la configuración `MYSQL_USER`, añádela.

Tercera advertencia: si tu archivo `.env` no tiene la configuración `MYSQL_USER`, añádela.

``` env
# Configuración de puertos
SVR_WEB_HTTP_PORT=8008           # Puerto HTTP
SVR_WEB_HTTPS_PORT=8009          # Puerto HTTPS
# Configuración de MySQL: modifícala con la información de tu MySQL local
MYSQL_HOST=host.docker.internal  # Usa host.docker.internal para que el contenedor acceda a los servicios del host
MYSQL_PORT=3306                  # Puerto local de MySQL
MYSQL_USER=rag_flow              # Nombre de usuario creado arriba; si no existe, añádelo
MYSQL_PASSWORD=infini_rag_flow   # Contraseña definida arriba
MYSQL_DBNAME=rag_flow            # Nombre de la base de datos

# Configuración de Redis: modifícala con la información de tu Redis local
REDIS_HOST=host.docker.internal  # Usa host.docker.internal para que el contenedor acceda a los servicios del host
REDIS_PORT=6379                  # Puerto local de Redis
REDIS_PASSWORD=                  # Si tu Redis no tiene contraseña, déjalo así; si tiene, escríbela
```

Ten en cuenta que, si tu Redis no tiene contraseña, también tendrás que modificar `ragflow/docker/service_conf.yaml.template` y sustituir `infini_rag_flow` por una cadena vacía.

Antes:
``` shell
redis:
  db: 1
  password: '${REDIS_PASSWORD:-infini_rag_flow}'
  host: '${REDIS_HOST:-redis}:6379'
```
Después:
``` shell
redis:
  db: 1
  password: '${REDIS_PASSWORD:-}'
  host: '${REDIS_HOST:-redis}:6379'
```

## Paso 5: iniciar el servicio RAGFlow
Ejecuta:
``` shell
docker-compose -f docker-compose.yml up -d
```
Si el comando se ejecuta correctamente, puedes usar `docker logs -n 20 -f docker-ragflow-cpu-1` para ver los logs del servicio `docker-ragflow-cpu-1`.

Si no aparecen errores en los logs, significa que el servicio RAGFlow se ha iniciado correctamente.

# Paso 5: registrar una cuenta
Puedes abrir `http://127.0.0.1:8008` en el navegador y hacer clic en `Sign Up` para registrar una cuenta.

Cuando el registro se complete, puedes hacer clic en `Sign In` para entrar en el servicio RAGFlow. Si quieres desactivar el registro y no permitir que otras personas creen cuentas, puedes establecer `REGISTER_ENABLED=0` en el archivo `.env` dentro de `ragflow/docker`.

``` dotenv
REGISTER_ENABLED=0
```
Después de modificarlo, reinicia el servicio RAGFlow:
``` shell
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

# Paso 6: configurar los modelos del servicio RAGFlow
Puedes abrir `http://127.0.0.1:8008` en el navegador, hacer clic en `Sign In` e iniciar sesión en el servicio RAGFlow. Luego haz clic en el `头像` de la esquina superior derecha para entrar en la página de configuración.
Primero, en la navegación lateral izquierda, haz clic en `模型供应商` para entrar en la página de configuración de modelos. En el cuadro `可选模型` de la derecha, elige `LLM`, selecciona de la lista el proveedor del modelo que uses, pulsa `添加` e introduce tu clave.
Después selecciona `TEXT EMBEDDING`, elige el proveedor correspondiente, pulsa `添加` e introduce tu clave.
Por último, refresca la página y en la lista `设置默认模型` selecciona por separado el modelo LLM y el modelo Embedding que quieras usar. Asegúrate de que tu clave tiene habilitados los servicios correspondientes. Por ejemplo, si el modelo Embedding que usas es de un proveedor concreto, tendrás que comprobar en la web oficial de ese proveedor si ese modelo requiere comprar un paquete de recursos.


# Segunda parte: configurar el servicio RAGFlow

# Paso 1: iniciar sesión en el servicio RAGFlow
Puedes abrir `http://127.0.0.1:8008` en el navegador y hacer clic en `Sign In` para entrar en el servicio RAGFlow.

Después haz clic en el `头像` de la esquina superior derecha para abrir la página de configuración. En la barra lateral izquierda, entra en la función `API` y luego haz clic en el botón `API Key`. Se abrirá una ventana emergente.

En esa ventana, haz clic en `Create new Key` para generar una `API Key`. Copia esa `API Key`, porque la necesitarás dentro de poco.

# Paso 2: configurarlo en el panel de control
Asegúrate de que tu panel de control está en la versión `0.8.7` o superior. Inicia sesión con una cuenta de superadministrador.

Primero debes habilitar la función de base de conocimiento. En la barra de navegación superior, haz clic en `参数字典` y, en el menú desplegable, entra en la página `系统功能配置`. Marca `知识库` y pulsa `保存配置`. Entonces verás la función `知识库` en la barra de navegación.

En la barra de navegación superior, haz clic en `模型配置` y luego en `知识库` en la barra lateral izquierda. En la lista, busca `RAG_RAGFlow` y haz clic en `编辑`.

En `服务地址`, escribe `http://IP-local-de-tu-ragflow:8008`. Por ejemplo, si la IP local de mi servicio RAGFlow es `192.168.1.100`, entonces escribiría `http://192.168.1.100:8008`.

En `API密钥`, escribe la `API Key` que copiaste antes.

Por último, haz clic en guardar.

# Paso 2: crear una base de conocimiento
Inicia sesión en el panel de control con una cuenta de superadministrador. En la barra de navegación superior, haz clic en `知识库` y, en la esquina inferior izquierda de la lista, pulsa `新增`. Introduce un nombre y una descripción para la base de conocimiento y guarda.

Para mejorar la comprensión y la capacidad de recuperación del modelo grande respecto a la base de conocimiento, se recomienda usar un nombre y una descripción significativos. Por ejemplo, si quieres crear una base de conocimiento sobre `公司介绍`, podrías usar como nombre `公司介绍` y como descripción `关于公司的相关信息例如公司基本信息、服务项目、联系电话、地址等。`.

Después de guardarla, verás esa base de conocimiento en la lista. Haz clic en `查看` sobre la base que acabas de crear para entrar en su página de detalles.

En la página de detalles, pulsa `新增` en la esquina inferior izquierda para subir documentos a la base de conocimiento.

Una vez subidos, podrás ver los documentos en la página de detalles. En ese momento puedes pulsar `解析` sobre cada documento para procesarlo.

Después del procesamiento, podrás revisar la información de los fragmentos generados. También puedes pulsar `召回测试` en la página de detalles para probar la capacidad de recuperación / búsqueda de la base de conocimiento.

# Paso 3: hacer que Xiaozhi use la base de conocimiento RAGFlow
Inicia sesión en el panel de control. En la barra de navegación superior, haz clic en `智能体`, busca el agente que quieres configurar y haz clic en `配置角色`.

A la izquierda del reconocimiento de intención, haz clic en `编辑功能`, se abrirá una ventana emergente. Dentro de esa ventana, selecciona la base de conocimiento que quieras añadir. Guarda y listo.
