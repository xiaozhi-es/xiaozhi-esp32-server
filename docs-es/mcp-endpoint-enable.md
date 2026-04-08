# Guía de despliegue y uso de puntos de acceso MCP

Este tutorial tiene 3 partes:
- 1、Cómo desplegar el servicio de punto de acceso MCP
- 2、Cómo configurar el punto de acceso MCP en un despliegue completo
- 3、Cómo configurar el punto de acceso MCP en un despliegue de un solo módulo

# 1、Cómo desplegar el servicio de punto de acceso MCP

## Paso 1: descargar el código fuente del proyecto de punto de acceso MCP

Abre en el navegador el [repositorio del proyecto de punto de acceso MCP](https://github.com/xinnan-tech/mcp-endpoint-server)

En la página, busca el botón verde `Code`, ábrelo y verás el botón `Download ZIP`.

Haz clic para descargar el código fuente comprimido. Después de descargarlo y descomprimirlo, es posible que el directorio se llame `mcp-endpoint-server-main`.
Debes renombrarlo a `mcp-endpoint-server`.

## Paso 2: arrancar el programa
Este proyecto es bastante simple y se recomienda ejecutarlo con Docker. Si no quieres usar Docker, puedes consultar [esta página](https://github.com/xinnan-tech/mcp-endpoint-server/blob/main/README_dev.md) para ejecutarlo desde el código fuente. A continuación se muestra el método con Docker:

```
# Entrar en el directorio raíz del código fuente del proyecto
cd mcp-endpoint-server

# Limpiar caché
docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server
docker rm mcp-endpoint-server
docker rmi ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest

# Iniciar el contenedor Docker
docker compose -f docker-compose.yml up -d
# Ver logs
docker logs -f mcp-endpoint-server
```

En este momento, los logs mostrarán algo parecido a esto:
```
250705 INFO-=====下面的地址分别是智控台/单模块MCP接入点地址====
250705 INFO-智控台MCP参数配置: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-单模块部署MCP接入点: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-=====请根据具体部署选择使用，请勿泄露给任何人======
```

Debes copiar las dos direcciones de interfaz:

Como estás usando un despliegue con Docker, no debes usar directamente las direcciones de arriba.

Como estás usando un despliegue con Docker, no debes usar directamente las direcciones de arriba.

Como estás usando un despliegue con Docker, no debes usar directamente las direcciones de arriba.

Primero copia esas direcciones en un borrador y averigua cuál es la IP de red local de tu ordenador. Por ejemplo, si la IP local de mi ordenador es `192.168.1.25`, entonces
mis direcciones originales:
```
智控台MCP参数配置: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
单模块部署MCP接入点: ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
```
deberían cambiarse a:
```
智控台MCP参数配置: http://192.168.1.25:8004/mcp_endpoint/health?key=abc
单模块部署MCP接入点: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

Una vez ajustadas, accede directamente desde el navegador a `智控台MCP参数配置`. Si el navegador muestra un código como este, significa que todo ha ido bien:
```
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

Guarda bien estas dos `direcciones de interfaz`, porque las necesitarás en el siguiente paso.

# 2、Cómo configurar el punto de acceso MCP en un despliegue completo
Primero debes habilitar la función de punto de acceso MCP. En el panel de control, haz clic en `参数字典` en la parte superior y luego entra en la página `系统功能配置` desde el menú desplegable. Marca `MCP接入点` y pulsa `保存配置`. Después, en la página `角色配置`, al pulsar `编辑功能`, podrás ver la función `mcp接入点`.

Si usas un despliegue completo, inicia sesión en el panel de control con una cuenta de administrador, haz clic en `参数字典` en la parte superior y entra en `参数管理`.

Luego busca el parámetro `server.mcp_endpoint`. En ese momento, su valor debería ser `null`.
Haz clic en editar, pega el valor de `智控台MCP参数配置` obtenido en el paso anterior dentro de `参数值` y guarda.

Si el guardado se completa correctamente, todo está bien y ya puedes revisar el efecto en el agente. Si no se guarda, probablemente el panel de control no pueda acceder al punto de acceso MCP, casi seguro por un firewall de red o porque no has rellenado correctamente la IP de red local.

# 3、Cómo configurar el punto de acceso MCP en un despliegue de un solo módulo

Si usas un despliegue de un solo módulo, abre tu archivo de configuración `data/.config.yaml`.
Busca `mcp_endpoint` dentro del archivo. Si no existe, añade esta configuración. Un ejemplo sería:
```
server:
  websocket: ws://tu-ip-o-dominio:puerto/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# Aquí puede haber más configuraciones...

mcp_endpoint: la-dirección-websocket-de-tu-punto-de-acceso
```
En este momento, pega en `mcp_endpoint` la dirección `单模块部署MCP接入点` obtenida en la sección “Cómo desplegar el servicio de punto de acceso MCP”. Quedaría así:

```
server:
  websocket: ws://tu-ip-o-dominio:puerto/xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# Aquí puede haber más configuraciones

mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

Después de configurarlo, al iniciar el despliegue de un solo módulo verás logs como estos:
```
250705[__main__]-INFO-初始化组件: vad成功 SileroVAD
250705[__main__]-INFO-初始化组件: asr成功 FunASRServer
250705[__main__]-INFO-OTA接口是          http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-视觉分析接口是     http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp接入点是        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket地址是    ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======上面的地址是websocket协议地址，请勿用浏览器访问=======
250705[__main__]-INFO-如想测试websocket请用谷歌浏览器打开test目录下的test_page.html
250705[__main__]-INFO-=============================================================
```

Como se ve arriba, si aparece un valor similar a `ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc` tras `mcp接入点是`, significa que la configuración se ha completado con éxito.
