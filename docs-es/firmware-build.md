# Compilación del firmware ESP32

## Paso 1: preparar tu dirección OTA

Si estás usando la versión `0.3.12` de este proyecto, tendrás una dirección OTA tanto si has hecho un despliegue simple del servidor como si has hecho un despliegue completo.

Como la forma de configurar la dirección OTA es diferente en el despliegue simple y en el despliegue completo, elige el método correspondiente a continuación:

### Si usas el despliegue simple del servidor
Ahora abre tu dirección OTA en el navegador. Por ejemplo, la mía es:
```
http://192.168.1.25:8003/xiaozhi/ota/
```
Si aparece “OTA接口运行正常，向设备发送的websocket地址是：ws://xxx:8000/xiaozhi/v1/”

Puedes usar el `test_page.html` incluido en el proyecto para comprobar si logra conectarse a la dirección WebSocket que muestra la página OTA.

Si no puedes acceder, tendrás que modificar la dirección `server.websocket` en tu archivo `.config.yaml`, reiniciar y volver a probar, hasta que `test_page.html` pueda acceder correctamente.

Cuando lo consigas, continúa con el paso 2.

### Si usas el despliegue completo
Ahora abre tu dirección OTA en el navegador. Por ejemplo, la mía es:
```
http://192.168.1.25:8002/xiaozhi/ota/
```

Si aparece “OTA接口运行正常，websocket集群数量：X”, entonces continúa con el paso 2.

Si aparece “OTA接口运行不正常”, probablemente todavía no hayas configurado la dirección `Websocket` en el `智控台`. En ese caso:

- 1、Inicia sesión en el `智控台` con una cuenta de superadministrador

- 2、Haz clic en `参数管理` en el menú superior

- 3、Busca el elemento `server.websocket` en la lista e introduce tu dirección `Websocket`. Por ejemplo, la mía es:

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

Después de configurarlo, vuelve a refrescar la dirección de la interfaz OTA en el navegador para comprobar si ya funciona. Si todavía no funciona, confirma otra vez que `Websocket` se haya iniciado correctamente y que su dirección esté bien configurada.

## Paso 2: configurar el entorno
Primero configura el entorno del proyecto siguiendo este tutorial: [《Windows搭建 ESP IDF 5.3.2开发环境以及编译小智》](https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

## Paso 3: abrir el archivo de configuración
Después de configurar el entorno de compilación, descarga el código fuente del proyecto `xiaozhi-esp32` de Xia Ge.

Puedes descargarlo aquí: [Código fuente del proyecto xiaozhi-esp32](https://github.com/78/xiaozhi-esp32)。

Después de descargarlo, abre el archivo `xiaozhi-esp32/main/Kconfig.projbuild`.

## Paso 4: modificar la dirección OTA

Busca el valor `default` de `OTA_URL` y cambia `https://api.tenclass.net/xiaozhi/ota/`
por tu propia dirección. Por ejemplo, si mi interfaz es `http://192.168.1.25:8002/xiaozhi/ota/`, debo sustituirla por esa.

Antes de la modificación:
```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```
Después de la modificación:
```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8002/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

## Paso 4: establecer los parámetros de compilación

Configura los parámetros de compilación:

```
# Entra en el directorio raíz de xiaozhi-esp32 desde la terminal
cd xiaozhi-esp32
# Por ejemplo, mi placa es una esp32s3, así que establezco esp32s3 como objetivo de compilación.
# Si tu placa es de otro modelo, sustitúyelo por el correspondiente.
idf.py set-target esp32s3
# Entrar en el menú de configuración
idf.py menuconfig
```

Una vez dentro del menú de configuración, entra en `Xiaozhi Assistant` y establece `BOARD_TYPE` al modelo concreto de tu placa.
Guarda los cambios, sal y vuelve a la terminal.

## Paso 5: compilar el firmware

```
idf.py build
```

## Paso 6: empaquetar el firmware `.bin`

```
cd scripts
python release.py
```

Cuando termine el comando anterior, se generará el archivo de firmware `merged-binary.bin` dentro del directorio `build` en la raíz del proyecto.
Ese `merged-binary.bin` es el firmware que debes grabar en el hardware.

Atención: si al ejecutar el segundo comando aparece un error relacionado con `zip`, puedes ignorarlo. Mientras en el directorio `build` se haya generado el archivo `merged-binary.bin`, no te afectará demasiado y puedes continuar.

## Paso 7: grabar el firmware
   Conecta el dispositivo ESP32 al ordenador y abre en Chrome la siguiente dirección:

```
https://espressif.github.io/esp-launchpad/
```

Abre este tutorial: [Herramienta Flash / grabación web del firmware (sin entorno IDF)](https://ccnphfhqs21z.feishu.cn/wiki/Zpz4wXBtdimBrLk25WdcXzxcnNS)。
Busca la sección `方式二：ESP-Launchpad 浏览器WEB端烧录` y sigue el tutorial a partir de `3. 烧录固件/下载到开发板`.

Después de grabar el firmware con éxito y de que el dispositivo se conecte a la red, despierta a Xiaozhi con la palabra de activación y presta atención a la salida de la consola del lado del servidor.

## Preguntas frecuentes
Estas son algunas preguntas frecuentes como referencia:

[1、¿Por qué Xiaozhi reconoce muchas palabras en coreano, japonés o inglés cuando hablo?](./FAQ.md)

[2、¿Por qué aparece “TTS 任务出错 文件不存在”?](./FAQ.md)

[3、TTS falla con frecuencia o agota el tiempo de espera](./FAQ.md)

[4、Puedo conectarme a mi servidor propio por Wi-Fi, pero no en modo 4G](./FAQ.md)

[5、¿Cómo mejorar la velocidad de respuesta de Xiaozhi?](./FAQ.md)

[6、Hablo despacio y Xiaozhi me interrumpe cuando hago pausas](./FAQ.md)

[7、Quiero usar Xiaozhi para controlar luces, aire acondicionado, encendido y apagado remoto, etc.](./FAQ.md)
