# Setup paso a paso

Notas para montarlo desde cero, en orden. Lo voy ejecutando línea a línea cuando tengo que volver a desplegar el proyecto.

## 0. Requisitos previos

- Docker Desktop arrancado.
- ngrok instalado desde `https://ngrok.com/download` y autenticado con mi cuenta (`ngrok config add-authtoken <token>` una sola vez). Plan gratis con dominio estático `tapping-widget-entering.ngrok-free.dev`.
- El kit `self-hosted-ai-starter-kit` clonado en `C:\self-hosted-ai-starter-kit-main\` (`https://github.com/n8n-io/self-hosted-ai-starter-kit`).

## 1. Arranque del kit en Docker

El kit trae 4 contenedores: `n8n`, `ollama`, `postgres-1` y `qdrant`. Solo uso los tres primeros (no hago RAG, así que Qdrant sobra). Como el kit usa nombres internos distintos para los servicios del compose, lo más práctico es arrancar todo y parar Qdrant a mano:

```powershell
cd C:\self-hosted-ai-starter-kit-main
docker compose up -d
docker stop qdrant
```

Compruebo que quedan los 3 en marcha:

```powershell
docker ps
```

n8n queda accesible en `http://localhost:5678`. La primera vez crea usuario y contraseña, las siguientes login normal.

## 2. Descarga de modelos en Ollama

El kit ya trae un contenedor llamado `ollama` con el binario instalado. Solo hay que entrar y bajarse los dos modelos del briefing diario. El chatbot va con Groq, así que para el chatbot no hace falta tirar de Ollama.

En estos comandos, el primer `ollama` es el **nombre del contenedor**, el segundo es el **binario** que ya está dentro:

```powershell
docker exec -it ollama ollama pull qwen2.5:1.5b
docker exec -it ollama ollama pull nomic-embed-text
```

Para comprobar que están:

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" | ConvertTo-Json -Depth 4
```

## 3. Túnel ngrok

Abro otra PowerShell aparte y lanzo el túnel hacia el puerto de n8n. La dejo abierta mientras uso el chatbot.

```powershell
ngrok http 5678 --domain=tapping-widget-entering.ngrok-free.dev
```

Si cierro esa ventana, el chatbot deja de recibir mensajes. El briefing diario y el panel HTML van por su cuenta, no dependen de ngrok.

Para verificar que el túnel está vivo:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" | ConvertTo-Json -Depth 5
```

Tiene que devolver un tunnel con `public_url` apuntando al dominio.

## 4. Credenciales en n8n

En `http://localhost:5678` → menú lateral → `Credentials` → `New`:

- **Telegram API**: token del bot que me dio BotFather.
- **Groq**: API key gratis sacada en `https://console.groq.com/keys`. Importante copiarla en cuanto la genera, después solo se ve el prefijo.

Pulso **Test** en las dos. Si pasan, sigo.

> Los nodos del briefing diario (`Embeddings Ollama` y `LLM Ollama`) NO necesitan credencial. Llaman a Ollama por HTTP directo a `http://ollama:11434` (la URL interna de Docker).

## 5. Despliegue del Apps Script

Abro la hoja Cosmic Briefing en Google Sheets → `Extensiones` → `Apps Script`. Pego el contenido de `google-apps-script/Code.gs` en el editor y le doy a:

```
Deploy → Manage deployments → (lápiz para editar) → Version: New version → Deploy
```

La URL `/exec` no cambia entre versiones. Para comprobar que el panel HTML responde, la pego en el navegador con `?action=dashboard` al final:

```
https://script.google.com/macros/s/AKfycbxyxBY-ktwHwRxIDpdzS38CyVp7s-h7sJXN7QGONkiiOLCaAcvz2nr-qI3OcOJ0bG5MXQ/exec?action=dashboard
```

Tienen que aparecer las tarjetas con los briefings.

## 6. Importación del workflow

En n8n → arriba a la izquierda → `+` → `Import from File` → selecciono `autor_workflow.json`.

Asigno credenciales en los dos nodos que las piden:

- `17. Telegram Trigger (chatbot)` → Telegram API.
- `Groq Chat Model (llama-3.3-70b)` → Groq.

El resto de nodos HTTP no necesitan credencial, llaman a APIs públicas.

Activo el workflow con el toggle de arriba a la derecha. Al activarse, n8n registra solo el webhook con Telegram a través de la URL de ngrok.

## 7. Pruebas funcionales

**Briefing manual**: en el editor, click en `Execute workflow` desde el Schedule trigger. En menos de un minuto llega el mensaje a Telegram con APOD, ISS, asteroides, lanzamientos, cielo, papers y noticias.

**Chatbot**: le escribo al bot por Telegram:

- «Hola» → contesta sin tirar de tools.
- «¿Qué dijo el último briefing?» → llama a `ultimos_briefings`.
- «Busca algo sobre SpaceX» → llama a `buscar_briefing`.

**Panel HTML**: el propio mensaje del briefing en Telegram trae el enlace al dashboard. Pinchando ahí se abre.

## 8. Resolución de problemas

- **El briefing no llega**: ejecuto nodo a nodo en n8n para ver dónde corta. Suele ser una API externa caída (NeoWs, Launch Library 2…). Como llevan `onError: continueRegularOutput`, no rompen el resto.
- **El bot no contesta**: miro `Executions` en n8n. Si no aparece la ejecución, el problema está antes. Compruebo el webhook con `https://api.telegram.org/bot<TOKEN>/getWebhookInfo` y miro si la URL coincide y si hay `last_error_message`.
- **403 «Provided secret is not valid»**: pasa si he tocado el webhook de Telegram a mano. Solución: desactivar y reactivar el workflow para que n8n re-registre el secret token.
- **404 al webhook**: lo más habitual es que ngrok no esté corriendo. Lanzo el comando del paso 3.
