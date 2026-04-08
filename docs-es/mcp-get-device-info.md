# Cómo obtener información del dispositivo con un método MCP

Este tutorial te guiará para usar un método MCP y obtener información del dispositivo.

Primer paso: personaliza tu archivo `agent-base-prompt.txt`

Copia el contenido del archivo `agent-base-prompt.txt` del directorio `xiaozhi-server` a tu directorio `data` y cámbiale el nombre a `.agent-base-prompt.txt`.

Segundo paso: modifica `data/.agent-base-prompt.txt`, busca la etiqueta `<context>` y añade dentro el siguiente contenido:
```
- **设备ID：** {{device_id}}
```

Después de añadirlo, el contenido de la etiqueta `<context>` en tu archivo `data/.agent-base-prompt.txt` debería quedar aproximadamente así:
```
<context>
【重要！以下信息已实时提供，无需调用工具查询，请直接使用：】
- **设备ID：** {{device_id}}
- **当前时间：** {{current_time}}
- **今天日期：** {{today_date}} ({{today_weekday}})
- **今天农历：** {{lunar_date}}
- **用户所在城市：** {{local_address}}
- **当地未来7天天气：** {{weather_info}}
</context>
```

Tercer paso: modifica `data/.config.yaml`, busca la configuración `agent-base-prompt`. Antes del cambio se ve así:
```
prompt_template: agent-base-prompt.txt
```
Cámbiala a:
```
prompt_template: data/.agent-base-prompt.txt
```

Cuarto paso: reinicia tu servicio `xiaozhi-server`.

Quinto paso: añade a tu método MCP un parámetro llamado `device_id`, de tipo `string` y con la descripción `设备ID`.

Sexto paso: vuelve a despertar a Xiaozhi, haz que invoque el método MCP y comprueba si tu método puede obtener `设备ID`.
