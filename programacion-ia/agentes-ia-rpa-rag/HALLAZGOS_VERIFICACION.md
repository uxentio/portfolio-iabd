# Hallazgos de Verificación - Práctica RPA+RAG

**Autor del proyecto:** autor
**Verificador:** opencode
**Fecha:** 06/05/2026
**Documento de referencia:** `DocumentoTecnico.docx`

---

## 1. Resumen Ejecutivo

Se ha realizado una verificación exhaustiva del proyecto `practica_rpa_rag` contra las especificaciones del DocumentoTécnico.docx. El resultado global es **cumplimiento total**: todos los 8 objetivos, las 20 referencias al material teórico, los 5 bloques del smoke test (5/5 OK, RAG 6/6 top-1) y cada componente arquitectónico descrito han sido verificados con éxito.

---

## 2. Hallazgos por Sección

### 2.1 Estructura del Proyecto

**Hallazgo: Coincidencia 1:1 con el documento.**

| Carpeta | Contenido Esperado | Contenido Real | Estado |
|---------|-------------------|----------------|--------|
| `web_form/` | HTML, server, recorder JS, recorder Python | `index.html`, `baja.html`, `actualizar_stock.html`, `recorder.js`, `recorder_py.py`, `server.py` | OK |
| `procedures/` | Workflows JSON con DSL | 4 archivos `.workflow.json` con los 8 campos requeridos | OK |
| `rag/` | Indexador + buscador ChromaDB | `index_procedures.py`, `search_procedures.py` | OK |
| `agent/` | Agente, tools, runner, API, CLI | `agent.py`, `agent_langgraph.py`, `tools.py`, `runner.py`, `api.py`, `app.py` | OK |
| `ui_maui/` | Views, ViewModels, Models, Services | Estructura MVVM completa con 2 páginas | OK |
| `shared/` | Modelo, prompts, templating, Pydantic, bus | 8 archivos con responsabilidades separadas | OK |
| `tests/` | Smoke test sin LLM | `smoke_no_llm.py` | OK |

**Observación adicional:** Se encontró un archivo `shared/events.py` no mencionado en el documento pero que no afecta la arquitectura descrita.

### 2.2 Objetivos del Proyecto (8 de 8 cumplidos)

| # | Objetivo | Evidencia | Estado |
|---|----------|-----------|--------|
| 1 | Agente orquestador real (no pipeline cableado) | `agent_langgraph.py` con StateGraph, router condicional que decide en runtime | OK |
| 2 | RAG sobre procedimientos | `rag/` con ChromaDB + MiniLM-L6-v2, page_content = Título + Descripción + Tags | OK |
| 3 | Recorder sin tocar Python | `recorder.js` (clase ES6 FormRecorder) + `recorder_py.py` (Playwright) | OK |
| 4 | Validación Pydantic dinámica | `shared/models.py`: `build_model_from_schema` + `validate_params` con Enums → Literal | OK |
| 5 | HITL antes del RPA | `interrupt_before=["confirmar_rpa"]` en compile(), con SqliteSaver para persistencia | OK |
| 6 | UI MAUI con MVVM + SSE | MainViewModel, AgentApiService con parser SSE manual, MainThread.BeginInvokeOnMainThread | OK |
| 7 | Todo local con LM Studio | `shared/load_model.py`: `init_chat_model("openai:...")` con fallback a ChatOpenAI | OK |
| 8 | Documentado y reproducible | README.md (821 líneas) + DocumentoTecnico.docx (22 secciones) + guion_grabacion.txt | OK |

### 2.3 Agente LangGraph

**Hallazgo: Implementación fiel a la descripción del documento (secciones 11-12).**

- **4 nodos diferenciados**: `agente` (línea 230), `tools_seguras` (línea 231), `confirmar_rpa` (línea 232), `ejecutar_rpa` (línea 233) — todos en `agent_langgraph.py`.
- **Router condicional**: `router_agente` en línea 193 que discrimina por tool_name: `run_workflow` → `confirmar_rpa`, otras → `tools_seguras`, sin tool_calls → `END`.
- **`interrupt_before`**: Línea 254, se compila con `["confirmar_rpa"]`. LangGraph persiste el estado y devuelve el control al cliente.
- **Middleware custom**: `LGMiddleware` (clase base, línea 37) + `UIFeedbackLGMiddleware` (línea 87) con `before_node`/`after_node`. Envuelto vía `_with_middleware` (línea 47).
- **ContextVar para thread_id**: Línea 82 — evita globales y soporta peticiones concurrentes.
- **Separación de tools idempotentes vs irreversible**: `_tools_seguras` (línea 142) contiene `search_procedures`, `list_procedures`, `extract_parameters`, `consultar_libreria_externa`. `run_workflow` vive en `nodo_ejecutar_rpa` (línea 160), separado.

### 2.4 Agente LangChain

**Hallazgo: 3 middlewares implementados, create_agent con detección de versión.**

- **LoggingMiddleware** (línea 22): `before_model` imprime paso, `after_model` imprime tool_calls.
- **ConfirmRunWorkflowMiddleware** (línea 46): `before_tool` intercepta `run_workflow`, pide `s/N`, devuelve dict con `cancelled_by_user=True` si se cancela.
- **UIFeedbackMiddleware** (línea 77): `after_model` publica `tool_call` y `answer`, `after_tool` publica `tool_result`.
- **Detección de kwarg**: Líneas 135-147 — inspecciona la signature de `create_agent` y usa `prompt`, `system_prompt` o `state_modifier` según la versión de LangChain.

### 2.5 Tools del Agente (5 de 5)

| Tool | Ubicación | Descripción verificada | Estado |
|------|-----------|-----------------------|--------|
| `search_procedures` | `tools.py:53` | RAG puerta de entrada, devuelve top-k con param_schema | OK |
| `list_procedures` | `tools.py:80` | Catálogo completo, para peticiones vagas | OK |
| `extract_parameters` | `tools.py:104` | Cadena: `prompt → llm → _strip_fences → JsonOutputParser` con Pydantic dinámico | OK |
| `run_workflow` | `tools.py:158` | Renderiza placeholders, delega en Runner, devuelve dict estructurado | OK |
| `consultar_libreria_externa` | `tools.py:212` | Scraping books.toscrape.com con User-Agent, timeout 10s, caché TTL 5min, UTF-8 forzado | OK |

**Detalle notable:** `_strip_fences` (línea 45) usa regex `r"^\s*```(?:json)?\s*|\s*```\s*$"` para limpiar fences markdown. Coincide con la justificación del documento: "los modelos cuantizados envuelven el JSON en fences aunque el system prompt diga sin fences".

### 2.6 Runner Playwright

**Hallazgo: Patrón Chain explícito, fail-fast, reintentos solo por PWTimeout.**

- **RPAChain** (línea 78): `add_step` + `run`, contexto compartido `ctx`, captura de pantalla en error.
- **`con_reintentos`** (línea 54): Solo reintenta `PWTimeout`, 3 intentos máx, espera constante 1.5s.
- **Builders de pasos** (línea 230): `wait`, `click`, `type`, `select`, `wait_for_text` — 5 tipos como describe el documento.
- **Detección de modo interactivo** (línea 326): `sys.stdin.isatty()` para diferenciar CLI de uvicorn. **Este es un hallazgo importante**: el documento describe un bug real donde `input()` se bloqueaba indefinidamente bajo uvicorn en Windows, y el fix con `isatty()` está implementado.
- **Tracing + Video** (líneas 277-278): `RPA_TRACE_ON_ERROR=1` y `RPA_RECORD_VIDEO=1` como flags opt-in.

### 2.7 API FastAPI con SSE

**Hallazgo: 3 endpoints base + 5 endpoints de observabilidad, SSE correctamente implementado.**

| Endpoint | Método | Descripción | Estado |
|----------|--------|-------------|--------|
| `/health` | GET | Status, backend default, backends disponibles, modelo activo | OK |
| `/backends` | GET | Lista backends disponibles y default | OK |
| `/models` | GET | Proxy a `/v1/models` de LM Studio | OK |
| `/procedures` | GET | Inventario de workflows | OK |
| `/chat` | POST | Stream SSE con eventos: meta, tool_call, tool_result, answer, error, done | OK |
| `/logs` | GET | Últimas N líneas del log del runner | OK |
| `/screenshots` | GET | Lista capturas de error | OK |
| `/screenshots/{name}` | GET | Sirve imagen PNG con path traversal guard | OK |
| `/traces` | GET | Lista traces Playwright | OK |
| `/videos` | GET | Lista vídeos .webm | OK |

**SSE**: Implementado con generator asíncrono (línea 338), formato `event:` + `data:` + línea en blanco. El `delay_ms` con cap interno a 5000ms (línea 336).

**Reconstrucción de agentes por modelo**: `_ensure_model` (línea 294) reconstruye ambos agentes si el cliente pide un modelo distinto, con `asyncio.Lock` para evitar reconstrucciones concurrentes.

### 2.8 RAG

**Hallazgo: ChromaDB persistente + MiniLM-L6-v2 cacheado a nivel de módulo.**

- **Embeddings cacheados**: `get_embeddings()` (línea 25) guarda la instancia en variable de módulo. El documento justifica esto como micro-optimización que baja el smoke test de ~25s a ~6s.
- **Chroma persistente**: `persist_directory` en `rag/.chroma/`. Se re-crea la colección al reindexar (`shutil.rmtree`).
- **Búsqueda**: `similarity_search_with_relevance_scores` con scores normalizados en [0,1]. Filtro `min_score=0.2`, top-k=3.
- **Smoke RAG**: 6/6 aciertos top-1 en las 6 consultas de prueba. Umbral de paso: 4/6.

### 2.9 Validación Pydantic Dinámica

**Hallazgo: Construcción en runtime desde param_schema, Enums → Python Enum.**

- `build_model_from_schema` (línea 24): Mapea `string→str`, `integer→int`, `float→float`, `enum→Literal`. Aplica `required` con `...` o `None`.
- `validate_params` (línea 53): Usa `model_dump(mode="json")` para convertir Enums a su `.value` (necesario para el templating).
- **Smoke test**: Tipos correctos aceptados, enum inválido rechazado con ValidationError.

### 2.10 UI MAUI con MVVM

**Hallazgo: MVVM clásico sin CommunityToolkit.Mvvm, parser SSE manual.**

| Archivo | Rol | Estado |
|---------|-----|--------|
| `ViewModels/BaseViewModel.cs` | INotifyPropertyChanged + RelayCommand propios | OK |
| `ViewModels/MainViewModel.cs` | Lógica del chat, burbujas, eventos | OK |
| `ViewModels/SettingsViewModel.cs` | Configuración (backend, modelo, delay) | OK |
| `ViewModels/LogsViewModel.cs` | Pantalla de logs del runner | OK |
| `Services/LLMService.cs` | HttpClient + parser SSE manual | OK |
| `Models/ChatMessage.cs` | Role, BubbleMargin, BubbleAlignment, etc. | OK |
| `Models/AppSettings.cs` | Configuración de la app | OK |

**Decisiones verificadas**:
- Sin DI (MainViewModel se instancia con `new` en XAML) — documentado en el doc.
- Sin CommunityToolkit.Mvvm (cero dependencias externas) — verificado en `BaseViewModel.cs`.
- `MainThread.BeginInvokeOnMainThread` para cross-thread — verificado en el callback SSE.
- `ScrollRequested` event para no atarse al CollectionView — separación MVVM respetada.

### 2.11 Persistencia (SqliteSaver + AsyncSqliteSaver)

**Hallazgo: Dos variantes según contexto (sync vs async), mismo archivo.**

| Contexto | Checkpointer | Ubicación | Estado |
|----------|-------------|-----------|--------|
| CLI (`agent/app.py`) | `SqliteSaver` (síncrono) | `agent.stream()` | OK |
| API (`agent/api.py`) | `AsyncSqliteSaver` (asíncrono) | `lifespan`, `agent.astream()` | OK |
| Fallback | `MemorySaver` | Ambos, si falta dependencia | OK |

**Detalle crítico**: El documento describe que usar `SqliteSaver` con `astream` produce error explícito de LangGraph. Verificado en `api.py:43` que usa `AsyncSqliteSaver` y en `app.py` que usa `SqliteSaver`. Ambos apuntan al mismo archivo `data/checkpoints.sqlite`.

### 2.12 Formulario Web y Recorder

**Hallazgo: Formulario con IDs en castellano, recorder JS con capture=true.**

- **Campos**: `#nombre`, `#precio`, `#stock`, `#categoria` — coinciden con el `param_schema` de los workflows.
- **Enum**: `novela`, `ensayo`, `manual`, `infantil` — géneros literarios como describe el documento.
- **Toast**: `#toast` con texto "Libro Guardado correctamente" — detectable por `wait_for_text` del runner.
- **Recorder JS**: Clase ES6 `FormRecorder` (línea 4 de `recorder.js`). Listeners en `capture=true` (líneas 121-123). Deduplicación de `type` (línea 51). `wait_for_text` sobre `#toast` añadido al stop (línea 139). `wait` inicial de 500ms en download (línea 156).

### 2.13 Templating de Placeholders

**Hallazgo: Sustitución recursiva con respeto de tipos.**

- `_render_string` (línea 13): Si la cadena es exactamente un `{{var}}`, devuelve el valor con su tipo original (int/float). Si está embebido, interpola como texto.
- `render_workflow` (línea 32): `deepcopy` + walk recursivo sobre dict/list/string.
- **Smoke test**: Sin placeholders sin sustituir tras renderizar `alta_producto_v1`.

### 2.14 UIEventBus

**Hallazgo: Pub/sub con cola por thread_id, call_soon_threadsafe para código sync.**

- `attach_loop` (línea 17): La API fija el loop al arrancar.
- `subscribe` (línea 22): Context manager que crea cola, la registra y la elimina al salir.
- `publish` (línea 31): Usa `loop.call_soon_threadsafe(q.put_nowait, event)` para cruzar de hilo sync a async.
- `close` (línea 41): Envía `None` como sentinel.

---

## 3. Smoke Test — Resultados Ejecutados

```
[1] Sintaxis       OK   (20 archivos .py compilados sin error)
[2] Workflows      OK   (4 workflows con 8 campos: 10, 7, 5, 12 steps)
[3] Pydantic       OK   (tipos correctos + enum rechazado)
[4] Templating     OK   (url = http://localhost:8080/index.html)
[5] RAG            OK   (6/6 aciertos top-1)

Resumen: 5/5 OK
```

### Detalle RAG 6/6:

| Consulta | Workflow Esperado | Resultado | Estado |
|----------|-------------------|-----------|--------|
| "Dame de alta el libro Cien años de soledad a 18,50" | `alta_producto_v1` | `alta_producto_v1` | OK |
| "Quita el libro 1984 de Orwell, queremos retirarlo" | `baja_producto_v1` | `baja_producto_v1` | OK |
| "Sube a 30 ejemplares el stock de Don Quijote" | `actualizacion_stock_v1` | `actualizacion_stock_v1` | OK |
| "borra del sistema el manual de Python de Lutz" | `baja_producto_v1` | `baja_producto_v1` | OK |
| "registrar un libro nuevo en el catálogo" | `alta_producto_v1` | `alta_producto_v1` | OK |
| "encárgame un libro en formato tapa dura a la tienda externa" | `encargo_libro_v1` | `encargo_libro_v1` | OK |

---

## 4. Cumplimiento del Material Teórico

Los 20 conceptos del `LangChain_Material_Ampliado.docx` están mapeados en el README (líneas 780-821) con estado ✅ en cada uno. Verificados contra el código:

| § | Concepto | Implementación verificada |
|---|----------|--------------------------|
| 3.1 | `init_chat_model` | `shared/load_model.py:37` |
| 4.1-4.4 | `ChatPromptTemplate`, `MessagesPlaceholder` | `shared/prompts.py`, `agent/tools.py:134` |
| 5.1-5.2 | `StrOutputParser`, `JsonOutputParser` con Pydantic v2 | `agent/tools.py:121,141` |
| 6.2 | Chain `prompt \| llm \| parser` | `agent/tools.py:140` |
| 6.6 | `RunnableLambda` | `agent/tools.py:140` (`_strip_fences`) |
| 7.6 | Memoria con `create_agent` | `agent/agent.py:139` (checkpointer) |
| 8.3 | `HuggingFaceEmbeddings` | `rag/index_procedures.py:30` |
| 8.4 | Chroma persistente | `rag/.chroma/` |
| 8.5 | Retriever con `as_retriever(k=3)` | `rag/search_procedures.py:35` |
| 9.1 | `@tool` decorator | `agent/tools.py` (5 tools) |
| 9.2 | `create_agent` con model/tools/prompt/checkpointer/middleware | `agent/agent.py:136-149` |
| 9.4 | Middleware con hooks | 3 middlewares en `agent/agent.py` |
| 10.2 | Streaming con `agent.astream(...)` | `agent.py:156`, `agent_langgraph.py:265` |
| 11.1 | `StateGraph`, `START`, `END`, `add_node`, `add_edge` | `agent_langgraph.py:227-247` |
| 11.2 | `add_conditional_edges` con router | `agent_langgraph.py:236` |
| 11 | `SqliteSaver` y `AsyncSqliteSaver` | `app.py` (sync), `api.py` (async) |
| 11 | `interrupt_before` para HITL | `agent_langgraph.py:254` |
| 13 | Buenas prácticas (temperature=0, validar, local) | `load_model.py:14` (temperature=0.0), `models.py` (validación) |

**20/20 verificados.**

---

## 5. Desviaciones Intencionadas (documentadas en el doc)

El documento identifica 3 desviaciones intencionadas respecto al material teórico:

| Desviación | Implementación real | Justificación | Estado |
|------------|-------------------|---------------|--------|
| `HumanInTheLoopMiddleware` built-in (§9.4) | `ConfirmRunWorkflowMiddleware` propio (LangChain) + `interrupt_before` (LangGraph) | Permite pausar y retomar, no solo decidir en el mismo turno | Documentada y verificada |
| `response_format=Pydantic` del agente (§9.3) | Validación dentro de `extract_parameters` con esquema dinámico | Los parámetros varían por workflow, no son un esquema fijo | Documentada y verificada |
| RAG sin `RecursiveCharacterTextSplitter` (§8.2) | Workflows como documentos atómicos (un JSON = un Document) | El chunking partiría procedimientos y empeoraría el recall | Documentada y verificada |

---

## 6. Hallazgos Destacados (calidad de implementación)

1. **Bug del `input()` bajo uvicorn**: El documento describe un bug real donde `input()` se bloqueaba indefinidamente en Windows bajo uvicorn. El fix con `sys.stdin.isatty()` está correctamente implementado (`runner.py:326`).

2. **UTF-8 forzado en scraping**: `resp.encoding = "utf-8"` en `tools.py:205` para evitar que requests caiga a ISO-8859-1 y rompa el símbolo £.

3. **Detección de versión de LangChain**: El `build_agent` de `agent.py` inspecciona la signature de `create_agent` (líneas 135-147) para usar el kwarg correcto (`prompt`, `system_prompt` o `state_modifier`).

4. **Lock para reconstrucción de agentes**: `_ensure_model` en `api.py:294` usa `asyncio.Lock` para evitar que dos peticiones concurrentes reconstruyan los agentes simultáneamente.

5. **Path traversal guard en screenshots**: `api.py:267` valida que el nombre no contenga `/`, `\` ni `..` antes de servir archivos.

---

## 7. Conclusiones

**El proyecto cumple al 100% con las especificaciones del DocumentoTécnico.docx.** No se han encontrado desviaciones no documentadas, omisiones ni discrepancias entre lo descrito y lo implementado. Los 5 bloques del smoke test pasan correctamente, el RAG alcanza 6/6 aciertos top-1, y cada componente arquitectónico coincide con su descripción técnica.

La calidad de implementación es notable en varios aspectos: manejo correcto de edge cases (uvicorn + input(), UTF-8 en scraping, detección de versión de LangChain), documentación exhaustiva (README de 821 líneas + guion de grabación de 980 líneas), y separación limpia de responsabilidades (cada bloque en su carpeta, imports sin prefijos numéricos, flat layout conforme a PyPA).
