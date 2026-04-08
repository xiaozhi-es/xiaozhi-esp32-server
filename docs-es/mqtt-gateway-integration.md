# Tutorial de despliegue de la pasarela MQTT

El proyecto `xiaozhi-esp32-server` puede integrarse con el proyecto de código abierto [xiaozhi-mqtt-gateway](https://github.com/78/xiaozhi-mqtt-gateway) de Xia Ge, con unas modificaciones sencillas, para permitir conexiones MQTT + UDP del hardware Xiaozhi.
Este tutorial se divide en tres partes. Según si usas un despliegue completo o un despliegue de un solo módulo, puedes seguir la parte correspondiente para conectar la pasarela MQTT:
- Primera parte: desplegar la pasarela MQTT
- Segunda parte: usar MQTT + UDP con hardware Xiaozhi en un despliegue completo
- Tercera parte: usar MQTT + UDP con hardware Xiaozhi en un despliegue de un solo módulo

## Preparación
Prepara la dirección de conexión `mqtt-websocket` de tu `xiaozhi-server`. Solo tienes que añadir `?from=mqtt_gateway` a tu dirección `websocket` original para obtener la dirección `mqtt-websocket`.

1、Si usas despliegue desde código fuente, tu dirección `mqtt-websocket` será:
```
ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway
```

2、Si usas despliegue con Docker, tu dirección `mqtt-websocket` será:
```
ws://你宿主机局域网IP:8000/xiaozhi/v1/?from=mqtt_gateway
```

## Aviso importante

Si tu despliegue está en un servidor, debes asegurarte de que los puertos `1883`, `8884` y `8007` estén abiertos al exterior. El puerto `8884` debe usar protocolo `UDP`; los demás, `TCP`.

Si tu despliegue está en un servidor, debes asegurarte de que los puertos `1883`, `8884` y `8007` estén abiertos al exterior. El puerto `8884` debe usar protocolo `UDP`; los demás, `TCP`.

Si tu despliegue está en un servidor, debes asegurarte de que los puertos `1883`, `8884` y `8007` estén abiertos al exterior. El puerto `8884` debe usar protocolo `UDP`; los demás, `TCP`.


## Primera parte: desplegar la pasarela MQTT

1. Clona el proyecto [xiaozhi-mqtt-gateway modificado](https://github.com/xinnan-tech/xiaozhi-mqtt-gateway.git):
```bash
git clone https://ghfast.top/https://github.com/xinnan-tech/xiaozhi-mqtt-gateway.git
cd xiaozhi-mqtt-gateway
```

2. Instala las dependencias:
```bash
npm install
npm install -g pm2
```

3. Configura `config.json`:
```bash
cp config/mqtt.json.example config/mqtt.json
```

4. Edita `config/mqtt.json` y sustituye dentro de `chat_servers` la dirección `mqtt-websocket` obtenida en la sección de preparación. Por ejemplo, si `xiaozhi-server` está desplegado desde código fuente, la configuración sería esta:

``` 
{
    "production": {
        "chat_servers": [
            "ws://127.0.0.1:8000/xiaozhi/v1/?from=mqtt_gateway"
        ]
    },
    "debug": false,
    "max_mqtt_payload_size": 8192,
    "mcp_client": {
        "capabilities": {
        },
        "client_info": {
            "name": "xiaozhi-mqtt-client",
            "version": "1.0.0"
        },
        "max_tools_count": 128
    }
}
```
5. Crea un archivo `.env` en la raíz del proyecto y define estas variables de entorno:
```
PUBLIC_IP=your-ip         # IP pública del servidor
MQTT_PORT=1883            # Puerto del servidor MQTT
UDP_PORT=8884             # Puerto del servidor UDP
API_PORT=8007             # Puerto de la API de administración
MQTT_SIGNATURE_KEY=test   # Clave de firma MQTT
SERVER_SECRET=Te1st12134  # Clave del servidor; debe coincidir con (server.secret) del panel de control o con (server.auth_key) de xiaozhi-server
```
Presta atención a la configuración `PUBLIC_IP`: asegúrate de que coincida con la IP pública real. Si tienes un dominio, usa el dominio.

`MQTT_SIGNATURE_KEY` es la clave usada para autenticar las conexiones MQTT. Se recomienda que sea relativamente compleja: idealmente 8 caracteres o más e incluyendo mayúsculas y minúsculas. Más adelante volverás a necesitar esta clave.

- No uses contraseñas simples como `123456`, `test`, etc.
- No uses contraseñas simples como `123456`, `test`, etc.
- No uses contraseñas simples como `123456`, `test`, etc.

`SERVER_SECRET` se usa para generar la información de autenticación de la conexión WebSocket.

1、Si usas un despliegue completo y en el panel de control el parámetro `server.auth.enabled` está configurado como `true`, entonces `SERVER_SECRET` debe coincidir con `server.secret` del panel de control.

2、Si usas un despliegue de un solo módulo y en tu archivo de configuración `server.auth.enabled` está configurado como `true`, entonces `SERVER_SECRET` debe coincidir con `server.auth_key` del archivo de configuración.


6. Iniciar la pasarela MQTT
```
# Iniciar el servicio
pm2 start ecosystem.config.js

# Ver logs
pm2 logs xz-mqtt
```

Cuando veas logs como los siguientes, significará que la pasarela MQTT se ha iniciado correctamente:
```
0|xz-mqtt  | 2025-09-11T12:14:48: MQTT 服务器正在监听端口 1883
0|xz-mqtt  | 2025-09-11T12:14:48: UDP 服务器正在监听 x.x.x.x:8884
```

Si necesitas reiniciar la pasarela MQTT, ejecuta:
```
pm2 restart xz-mqtt
```

## Segunda parte: usar conexión MQTT + UDP del hardware Xiaozhi en un despliegue completo

Consulta el número de versión que aparece en la parte inferior de la página principal del panel de control y confirma que sea `0.7.7` o superior. Si no lo es, tendrás que actualizar el panel de control.

1. En la parte superior del panel de control, haz clic en `参数管理`, busca `server.mqtt_gateway`, pulsa editar e introduce `PUBLIC_IP` + `:` + `MQTT_PORT` tal como lo configuraste en tu archivo `.env`. Por ejemplo:
```
192.168.0.7:1883
```
2. En la parte superior del panel de control, haz clic en `参数管理`, busca `server.mqtt_signature_key`, pulsa editar e introduce el valor `MQTT_SIGNATURE_KEY` definido en tu archivo `.env`.

3. En la parte superior del panel de control, haz clic en `参数管理`, busca `server.udp_gateway`, pulsa editar e introduce `PUBLIC_IP` + `:` + `UDP_PORT` tal como lo configuraste en tu archivo `.env`. Por ejemplo:
```
192.168.0.7:8884
```
4. En la parte superior del panel de control, haz clic en `参数管理`, busca `server.mqtt_manager_api`, pulsa editar e introduce `PUBLIC_IP` + `:` + `UDP_PORT` tal como lo configuraste en tu archivo `.env`. Por ejemplo:
```
192.168.0.7:8007
```

Después de completar la configuración anterior, puedes usar `curl` para comprobar si tu dirección OTA está distribuyendo la configuración MQTT. Sustituye `http://localhost:8002/xiaozhi/ota/` por tu dirección OTA real:
```
curl 'http://localhost:8002/xiaozhi/ota/' \
  -H 'Content-Type: application/json' \
  -H 'Client-Id: 7b94d69a-9808-4c59-9c9b-704333b38aff' \
  -H 'Device-Id: 11:22:33:44:55:66' \
  --data-raw $'{\n  "application": {\n    "version": "1.0.1",\n    "elf_sha256": "1"\n  },\n  "board": {\n    "mac": "11:22:33:44:55:66"\n  }\n}'
```

Si el contenido devuelto incluye configuración relacionada con `mqtt`, significa que la configuración fue correcta. Por ejemplo:

```
{"server_time":{"timestamp":1757567894012,"timeZone":"Asia/Shanghai","timezone_offset":480},"activation":{"code":"460609","message":"http://xiaozhi.server.com\n460609","challenge":"11:22:33:44:55:66"},"firmware":{"version":"1.0.1","url":"http://xiaozhi.server.com:8002/xiaozhi/otaMag/download/NOT_ACTIVATED_FIRMWARE_THIS_IS_A_INVALID_URL"},"websocket":{"url":"ws://192.168.4.23:8000/xiaozhi/v1/"},"mqtt":{"endpoint":"192.168.0.7:1883","client_id":"GID_default@@@11_22_33_44_55_66@@@7b94d69a-9808-4c59-9c9b-704333b38aff","username":"eyJpcCI6IjA6MDowOjA6MDowOjA6MSJ9","password":"Y8XP9xcUhVIN9OmbCHT9ETBiYNE3l3Z07Wk46wV9PE8=","publish_topic":"device-server","subscribe_topic":"devices/p2p/11_22_33_44_55_66"}}
```

Como la información MQTT se distribuye a través de la dirección OTA, basta con asegurarte de que el dispositivo puede conectarse correctamente a la dirección OTA del servidor y luego reiniciarlo y despertarlo.

Después del despertar, revisa los logs de `mqtt-gateway` para confirmar si aparece un log de conexión correcta.
```
pm2 logs xz-mqtt
```

## Tercera parte: usar conexión MQTT + UDP del hardware Xiaozhi en un despliegue de un solo módulo

Abre tu archivo `data/.config.yaml`, busca `mqtt_gateway` dentro de `server` e introduce `PUBLIC_IP` + `:` + `MQTT_PORT` tal como lo configuraste en `.env`. Por ejemplo:
```
192.168.0.7:1883
```
En `server`, busca `mqtt_signature_key` e introduce el valor `MQTT_SIGNATURE_KEY` definido en tu `.env`.

En `server`, busca `udp_gateway` e introduce `PUBLIC_IP` + `:` + `UDP_PORT` tal como lo configuraste en `.env`. Por ejemplo:
```
192.168.0.7:8884
```

Después de completar la configuración anterior, puedes usar `curl` para comprobar si tu dirección OTA está distribuyendo la configuración MQTT. Sustituye `http://localhost:8002/xiaozhi/ota/` por tu dirección OTA real:
```
curl 'http://localhost:8002/xiaozhi/ota/' \
  -H 'Device-Id: 11:22:33:44:55:66' \
  --data-raw $'{\n  "application": {\n    "version": "1.0.1",\n    "elf_sha256": "1"\n  },\n  "board": {\n    "mac": "11:22:33:44:55:66"\n  }\n}'
```

Si el contenido devuelto incluye configuración relacionada con `mqtt`, significa que la configuración fue correcta. Por ejemplo:
```
{"server_time":{"timestamp":1758781561083,"timeZone":"GMT+08:00","timezone_offset":480},"activation":{"code":"527111","message":"http://xiaozhi.server.com\n527111","challenge":"11:22:33:44:55:66"},"firmware":{"version":"1.0.1","url":"http://xiaozhi.server.com:8002/xiaozhi/otaMag/download/NOT_ACTIVATED_FIRMWARE_THIS_IS_A_INVALID_URL"},"websocket":{"url":"ws://192.168.1.15:8000/xiaozhi/v1/"},"mqtt":{"endpoint":"192.168.1.15:1883","client_id":"GID_default@@@11_22_33_44_55_66@@@11_22_33_44_55_66","username":"eyJpcCI6IjE5Mi4xNjguMS4xNSJ9","password":"fjAYs49zTJecWqJ3jBt+kqxVn/x7vkXRAc85ak/va7Y=","publish_topic":"device-server","subscribe_topic":"devices/p2p/11_22_33_44_55_66"}}
```

Como la información MQTT se distribuye a través de la dirección OTA, basta con asegurarte de que el dispositivo puede conectarse correctamente a la dirección OTA del servidor y luego reiniciarlo y despertarlo.

Después del despertar, revisa los logs de `mqtt-gateway` para confirmar si aparece un log de conexión correcta.
```
pm2 logs xz-mqtt
```
