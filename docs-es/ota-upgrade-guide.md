# Guía de configuración de actualización automática OTA del firmware en un despliegue de un solo módulo

Este tutorial te guiará para configurar la actualización automática OTA del firmware en un escenario de **despliegue de un solo módulo**, de modo que el firmware del dispositivo pueda actualizarse automáticamente.

Si ya estás usando un **despliegue completo**, puedes ignorar este tutorial.

## Descripción de la función

En el despliegue de un solo módulo, `xiaozhi-server` incorpora gestión OTA del firmware. Puede detectar automáticamente la versión del dispositivo y enviar el firmware de actualización. El sistema empareja y distribuye automáticamente la versión más reciente según el modelo del dispositivo y su versión actual.

## Requisitos previos

- Ya has realizado correctamente el **despliegue de un solo módulo** y `xiaozhi-server` está en ejecución
- El dispositivo puede conectarse al servidor con normalidad

## Paso 1: preparar los archivos de firmware

### 1. Crear el directorio donde se almacenará el firmware

Los archivos de firmware deben colocarse en el directorio `data/bin/`. Si ese directorio no existe, créalo manualmente:

```bash
mkdir -p data/bin
```

### 2. Reglas de nomenclatura del firmware

El archivo de firmware debe seguir este formato de nombre:

```
{modelo_del_dispositivo}_{versión}.bin
```

**Explicación de las reglas de nombre:**
- `modelo_del_dispositivo`: el nombre del modelo del dispositivo, por ejemplo `lichuang-dev`, `bread-compact-wifi`, etc.
- `versión`: la versión del firmware. Debe empezar por un número y puede incluir números, letras, puntos, guiones bajos y guiones medios, por ejemplo `1.6.6`, `2.0.0`, etc.
- La extensión del archivo debe ser `.bin`

**Ejemplos de nombre:**
```
bread-compact-wifi_1.6.6.bin
lichuang-dev_2.0.0.bin
```

### 3. Colocar el archivo de firmware

Copia el archivo de firmware preparado (archivo `.bin`) al directorio `data/bin/`:

Importante, repetido tres veces: el archivo `.bin` usado para la actualización es `xiaozhi.bin`, no el archivo de firmware completo `merged-binary.bin`.

Importante, repetido tres veces: el archivo `.bin` usado para la actualización es `xiaozhi.bin`, no el archivo de firmware completo `merged-binary.bin`.

Importante, repetido tres veces: el archivo `.bin` usado para la actualización es `xiaozhi.bin`, no el archivo de firmware completo `merged-binary.bin`.

```bash
cp xiaozhi.bin data/bin/设备型号_版本号.bin
```

Por ejemplo:
```bash
cp xiaozhi.bin data/bin/bread-compact-wifi_1.6.6.bin
```

## Paso 2: configurar la dirección de acceso público (solo necesaria para despliegues públicos)

**Atención: este paso solo se aplica al despliegue público de un solo módulo.**

Si tu `xiaozhi-server` está desplegado públicamente (con IP pública o dominio), **debes** configurar el parámetro `server.vision_explain`, porque la dirección de descarga del firmware OTA usará el dominio y el puerto definidos ahí.

Si tu despliegue es dentro de una red local, puedes omitir este paso.

### ¿Por qué hay que configurar este parámetro?

En el despliegue de un solo módulo, cuando el sistema genera la dirección de descarga del firmware, usa como base el dominio y el puerto de la configuración `vision_explain`. Si no lo configuras o lo configuras mal, el dispositivo no podrá acceder a la dirección de descarga del firmware.

### Método de configuración

Abre `data/.config.yaml`, busca el bloque de configuración `server` y establece el parámetro `vision_explain`:

```yaml
server:
  vision_explain: http://tu-dominio-o-ip:puerto/mcp/vision/explain
```

**Ejemplos de configuración:**

Despliegue en red local (predeterminado):
```yaml
server:
  vision_explain: http://192.168.1.100:8003/mcp/vision/explain
```

Despliegue con dominio público:
```yaml
server:
  vision_explain: http://yourdomain.com:8003/mcp/vision/explain
```

### Notas

- El dominio o la IP deben ser accesibles desde el dispositivo
- Si usas Docker, no puedes usar direcciones internas de Docker (como `127.0.0.1` o `localhost`)
- Si usas nginx como proxy inverso, escribe la dirección y el puerto externos, no el puerto interno en el que se ejecuta este proyecto


## Preguntas frecuentes

### 1. El dispositivo no recibe la actualización del firmware

**Posibles causas y soluciones:**

- Comprueba si el nombre del archivo de firmware sigue la regla: `{modelo}_{versión}.bin`
- Comprueba si el archivo de firmware está correctamente colocado en `data/bin/`
- Comprueba si el modelo del dispositivo coincide con el modelo incluido en el nombre del archivo
- Comprueba si la versión del firmware es superior a la versión actual del dispositivo
- Revisa los logs del servidor para confirmar que la petición OTA se está procesando correctamente

### 2. El dispositivo informa que no puede acceder a la dirección de descarga

**Posibles causas y soluciones:**

- Comprueba si el dominio o la IP configurados en `server.vision_explain` son correctos
- Confirma que el puerto está bien configurado (por defecto, `8003`)
- Si el despliegue es público, asegúrate de que el dispositivo puede acceder a esa dirección pública
- Si usas Docker, asegúrate de no estar usando una dirección interna (`127.0.0.1`)
- Comprueba si el firewall tiene abierto el puerto correspondiente
- Si usas nginx como proxy inverso, escribe la dirección y el puerto externos, no el puerto interno de este proyecto

### 3. Cómo confirmar la versión actual del dispositivo

Consulta los logs de la petición OTA. En ellos aparecerá la versión reportada por el dispositivo:

```
[ota_handler] - 设备 AA:BB:CC:DD:EE:FF 固件已是最新: 1.6.6
```

### 4. El archivo de firmware no surte efecto después de colocarlo

El sistema tiene un tiempo de caché de 30 segundos (por defecto). Puedes:
- Esperar 30 segundos antes de volver a hacer que el dispositivo lance una petición OTA
- Reiniciar el servicio `xiaozhi-server`
- Ajustar la configuración `firmware_cache_ttl` a un valor más corto
