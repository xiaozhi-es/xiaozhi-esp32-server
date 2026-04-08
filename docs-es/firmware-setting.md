# Configurar un servidor personalizado a partir del firmware compilado por Xia Ge

## Paso 1: confirmar la versión
Flashea una [versión de firmware 1.6.1 o superior](https://github.com/78/xiaozhi-esp32/releases) ya compilada por Xia Ge.

## Paso 2: preparar tu dirección OTA
Si seguiste el tutorial usando el despliegue de todos los módulos, deberías tener una dirección OTA.

Ahora abre tu dirección OTA en el navegador. Por ejemplo, la mía es:
```
https://2662r3426b.vicp.fun/xiaozhi/ota/
```

Si aparece “La interfaz OTA funciona con normalidad. Número de clústeres WebSocket: X”, puedes continuar.

Si aparece “Mal funcionamiento de la interfaz OTA”, probablemente todavía no hayas configurado la dirección `Websocket` en el `智控台`. En ese caso:

- 1、Inicia sesión en el `Panel de control inteligente` con una cuenta de superadministrador

- 2、Haz clic en `Gestión de parámetros` en el menú superior

- 3、Busca el elemento `server.websocket` en la lista e introduce tu dirección `Websocket`. Por ejemplo, la mía es:

```
wss://2662r3426b.vicp.fun/xiaozhi/v1/
```

Después de configurarlo, vuelve a refrescar en el navegador la dirección de la interfaz OTA para comprobar si ya funciona correctamente. Si todavía no funciona, confirma otra vez que `Websocket` se haya iniciado bien y que su dirección esté configurada.

## Paso 3: entrar en modo de aprovisionamiento de red
Pon el dispositivo en modo de aprovisionamiento de red. En la parte superior de la página, haz clic en “Opciones avanzadas”, introduce la dirección `ota` de tu servidor, guarda los cambios y reinicia el dispositivo.
![Consulta la configuración de la dirección OTA](../docs/images/firmware-setting-ota.png)

## Paso 4: despertar a Xiaozhi y revisar los logs

Despierta a Xiaozhi y comprueba si los logs se están mostrando correctamente.


## Preguntas frecuentes
Estas son algunas preguntas frecuentes como referencia:

[1、¿Por qué Xiaozhi reconoce muchas palabras en coreano, japonés o inglés cuando hablo?](./FAQ.md)

[2、¿Por qué aparece “Error de la tarea TTS: el archivo no existe.”?](./FAQ.md)

[3、TTS falla con frecuencia o agota el tiempo de espera](./FAQ.md)

[4、Puedo conectarme a mi servidor propio por Wi-Fi, pero no en modo 4G](./FAQ.md)

[5、¿Cómo mejorar la velocidad de respuesta de Xiaozhi?](./FAQ.md)

[6、Hablo despacio y Xiaozhi me interrumpe cuando hago pausas](./FAQ.md)

[7、Quiero usar Xiaozhi para controlar luces, aire acondicionado, encendido y apagado remoto, etc.](./FAQ.md)
