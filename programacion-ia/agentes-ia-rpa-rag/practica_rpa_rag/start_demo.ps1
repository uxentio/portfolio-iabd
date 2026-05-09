# start_demo.ps1
# Arranca toda la demo en Windows: comprueba prerequisitos, crea venv,
# instala deps, indexa el RAG, levanta web_form y la API en ventanas
# nuevas, compila y lanza el cliente MAUI, abre las páginas web del
# formulario y la URL de health de la API. Lo único que NO automatiza
# es LM Studio (es una app de escritorio con servidor local que el
# usuario debe arrancar a mano cargando el modelo).
#
# Uso:
#     powershell -ExecutionPolicy Bypass -File .\start_demo.ps1
#
# Si el proceso falla en algún punto, imprime un mensaje claro y aborta.

$ErrorActionPreference = "Stop"

# Defensa contra sesiones de PowerShell con auto-loading de módulos
# desactivado o con perfiles que han descargado módulos básicos. Si los
# Import-Module fallan (instalación corrupta), el script aborta limpio.
try {
    Import-Module Microsoft.PowerShell.Utility -ErrorAction Stop
    Import-Module Microsoft.PowerShell.Management -ErrorAction Stop
} catch {
    [Console]::Error.WriteLine("ERROR: no pude cargar los modulos basicos de PowerShell.")
    [Console]::Error.WriteLine("Causa probable: sesion con `$PSModuleAutoLoadingPreference = 'None'.")
    [Console]::Error.WriteLine("Solucion: abre una ventana nueva de PowerShell y vuelve a lanzar el script.")
    exit 1
}

$RAIZ = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RAIZ

function Escribe-Titulo {
    param([string]$Texto)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host $Texto -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Escribe-Paso {
    param([string]$Texto)
    Write-Host "[*] $Texto" -ForegroundColor Yellow
}

function Escribe-Ok {
    param([string]$Texto)
    Write-Host "    OK $Texto" -ForegroundColor Green
}

function Escribe-Aviso {
    param([string]$Texto)
    Write-Host "    AVISO $Texto" -ForegroundColor DarkYellow
}

function Escribe-Error {
    param([string]$Texto)
    Write-Host "    ERROR $Texto" -ForegroundColor Red
}


# 1. Verificar Python 3.11+ y avisar si la versión es muy nueva (sin wheels)
# Si ya hay un venv sano, su python es lo que importa (no el del PATH).
Escribe-Titulo "1. Comprobando prerequisitos"

$venvPathTmp = Join-Path $RAIZ ".venv"
$venvCfgTmp = Join-Path $venvPathTmp "pyvenv.cfg"
$pythonVenvTmp = Join-Path $venvPathTmp "Scripts\python.exe"
$venvYaExisteSano = (Test-Path $pythonVenvTmp) -and (Test-Path $venvCfgTmp)

if ($venvYaExisteSano) {
    # Hay un venv sano: uso SU python para el chequeo de versión.
    Escribe-Paso "Python del venv existente (.venv)..."
    try {
        $pythonVersion = & $pythonVenvTmp --version 2>&1
        if ($LASTEXITCODE -ne 0) { throw "el venv no responde" }
        Escribe-Ok "$pythonVersion (del venv)"
        $versionStr = ($pythonVersion -replace "Python ", "").Trim()
        $partes = $versionStr.Split(".")
        $mayor = [int]$partes[0]
        $menor = [int]$partes[1]
        if ($mayor -eq 3 -and $menor -ge 14) {
            Escribe-Aviso "El venv usa Python $versionStr, muy reciente. Si pip falla por wheels"
            Escribe-Aviso "ausentes, recrea el venv con: Remove-Item -Recurse -Force .venv; py -3.12 -m venv .venv"
        }
    } catch {
        Escribe-Aviso "No pude consultar la versión del venv: $_"
    }
} else {
    # Sin venv: compruebo el python global, que es el que se usará para crearlo.
    Escribe-Paso "Python 3.11 a 3.13 (rango con wheels precompilados)..."
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) { throw "python no responde" }
        Escribe-Ok "$pythonVersion"
        $versionStr = ($pythonVersion -replace "Python ", "").Trim()
        $partes = $versionStr.Split(".")
        $mayor = [int]$partes[0]
        $menor = [int]$partes[1]
        if ($mayor -lt 3 -or ($mayor -eq 3 -and $menor -lt 11)) {
            Escribe-Aviso "Se recomienda Python 3.11 o superior. Detectada $versionStr."
        } elseif ($mayor -eq 3 -and $menor -ge 14) {
            Escribe-Aviso "Python $versionStr es muy nuevo. Muchos paquetes (torch, chromadb, pydantic-core)"
            Escribe-Aviso "no tienen wheels precompilados para 3.14+ y pip intentará compilar desde source,"
            Escribe-Aviso "lo que suele fallar sin Visual C++ Build Tools. Recomendado: Python 3.11, 3.12 o 3.13."
            Write-Host ""
            Write-Host "    Para instalar 3.12 (recomendado):" -ForegroundColor White
            Write-Host "    winget install Python.Python.3.12" -ForegroundColor Gray
            Write-Host ""
            Write-Host "    Si quieres seguir con $versionStr y ver hasta dónde llega, pulsa Enter." -ForegroundColor White
            Write-Host "    Mejor opción: aborta con Ctrl+C, instala 3.12 y crea el venv con:" -ForegroundColor White
            Write-Host "        Remove-Item -Recurse -Force .venv" -ForegroundColor Gray
            Write-Host "        py -3.12 -m venv .venv" -ForegroundColor Gray
            Write-Host "    Y vuelve a lanzar el script." -ForegroundColor White
            $null = Read-Host "    [Enter para continuar]"
        }
    } catch {
        Escribe-Error "Python no está instalado o no está en PATH. Descárgalo desde https://www.python.org/downloads/"
        exit 1
    }
}

# 2. Verificar .NET 8 SDK (warning si falta, MAUI es opcional)
Escribe-Paso ".NET 8 SDK (opcional, para el cliente MAUI)..."
$tieneDotnet = $false
try {
    $dotnetVersion = & dotnet --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Escribe-Ok "dotnet $dotnetVersion"
        $tieneDotnet = $true
    }
} catch {}
if (-not $tieneDotnet) {
    Escribe-Aviso ".NET SDK no detectado. La UI MAUI no se podrá compilar (puedes seguir sin ella usando la CLI)."
}


# 3. Crear / activar venv (con detección de venv corrupto)
Escribe-Titulo "2. Entorno virtual y dependencias"
$venvPath = Join-Path $RAIZ ".venv"
$venvCfg = Join-Path $venvPath "pyvenv.cfg"
$pythonVenv = Join-Path $venvPath "Scripts\python.exe"

# Un venv válido tiene Scripts/python.exe Y pyvenv.cfg. Si falta cualquiera
# de los dos, lo borro y lo regenero. Esto cubre el caso de un venv heredado
# de otra ubicación o un venv que se quedó a medias.
$venvSano = (Test-Path $pythonVenv) -and (Test-Path $venvCfg)

if ((Test-Path $venvPath) -and -not $venvSano) {
    Escribe-Aviso ".venv existe pero está incompleto (falta pyvenv.cfg o python.exe). Lo recreo."
    try {
        Remove-Item -Recurse -Force $venvPath
    } catch {
        Escribe-Error "No pude borrar el venv corrupto: $_"
        exit 1
    }
}

if (-not (Test-Path $venvPath)) {
    Escribe-Paso "Creando venv en .venv..."
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Escribe-Error "No pude crear el venv."
        exit 1
    }
    Escribe-Ok "venv creado."
} else {
    Escribe-Ok "venv ya existe y está sano."
}

if (-not (Test-Path $pythonVenv)) {
    Escribe-Error "No encuentro $pythonVenv tras crear el venv."
    exit 1
}

# 4. Instalar dependencias en el venv
# - Purgo la caché de pip antes para evitar 'Cache entry deserialization failed'
#   que aparece cuando hay entradas viejas con formato distinto al actual.
# - Uso --prefer-binary para que pip no intente compilar desde source si hay wheel.
Escribe-Paso "Limpiando caché de pip..."
& $pythonVenv -m pip cache purge 2>&1 | Out-Null

Escribe-Paso "Actualizando pip a la última versión..."
& $pythonVenv -m pip install --upgrade pip --quiet --no-cache-dir

Escribe-Paso "Instalando paquetes de requirements.txt (la primera vez tarda 5-10 min)..."
& $pythonVenv -m pip install -r requirements.txt --quiet --prefer-binary
if ($LASTEXITCODE -ne 0) {
    Escribe-Error "Falló pip install. Causas habituales:"
    Write-Host "    - Python muy nuevo (3.14+): faltan wheels precompilados. Usa 3.11/3.12/3.13." -ForegroundColor White
    Write-Host "    - Faltan Visual C++ Build Tools (compilación desde source)." -ForegroundColor White
    Write-Host "    - Sin conexión a PyPI o proxy bloqueando." -ForegroundColor White
    exit 1
}
Escribe-Ok "Dependencias instaladas."

# 5. Playwright Chromium
Escribe-Paso "Comprobando navegador de Playwright..."
& $pythonVenv -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Escribe-Aviso "playwright install devolvió código no cero. Si Chromium ya estaba, ignóralo."
} else {
    Escribe-Ok "Chromium listo."
}

# 6. Indexar el RAG si no existe
Escribe-Titulo "3. Índice RAG"
$chromaPath = Join-Path $RAIZ "rag\.chroma"
if (-not (Test-Path $chromaPath)) {
    Escribe-Paso "Indexando workflows en ChromaDB (primer arranque)..."
    & $pythonVenv rag\index_procedures.py
    if ($LASTEXITCODE -ne 0) {
        Escribe-Error "Falló la indexación del RAG."
        exit 1
    }
    Escribe-Ok "Índice creado en rag\.chroma."
} else {
    Escribe-Ok "Índice RAG ya presente. Si has añadido workflows, vuelve a indexar manualmente."
}

# 7. .env si no existe
$envFile = Join-Path $RAIZ ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item -Path (Join-Path $RAIZ ".env.example") -Destination $envFile
    Escribe-Aviso "Creado .env desde .env.example. Revisa OPENAI_MODEL para que coincida con tu LM Studio."
}


# 8. Lanzar web_form en ventana nueva
Escribe-Titulo "4. Levantando servidores"
Escribe-Paso "Abriendo nueva ventana para el servidor del formulario web (puerto 8080)..."
$cmdWebForm = "Set-Location '$RAIZ'; & '$pythonVenv' web_form\server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdWebForm | Out-Null
Escribe-Ok "Servidor web_form lanzado."

# 9. Lanzar API en ventana nueva
Escribe-Paso "Abriendo nueva ventana para la API (uvicorn, puerto 8001)..."
$cmdApi = "Set-Location '$RAIZ'; & '$pythonVenv' -m uvicorn agent.api:app --port 8001"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdApi | Out-Null
Escribe-Ok "API lanzada."

# 10. Esperar y comprobar conectividad de los dos servidores
# Subido a 90s porque uvicorn tarda en cargar torch/chromadb la primera vez,
# sobre todo en CPU lenta o sin caché de pip.
Escribe-Paso "Esperando a que arranquen (máx 90s)..."
$webOk = $false
$apiOk = $false
for ($i = 1; $i -le 45; $i++) {
    Start-Sleep -Seconds 2
    if (-not $webOk) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:8080/index.html" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $webOk = $true }
        } catch {}
    }
    if (-not $apiOk) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $apiOk = $true }
        } catch {}
    }
    if ($webOk -and $apiOk) { break }
}
if ($webOk) { Escribe-Ok "web_form responde en :8080." } else { Escribe-Aviso "web_form no responde aún en :8080 (sigue cargando, mira la ventana)." }
if ($apiOk) { Escribe-Ok "API responde en :8001/health." } else { Escribe-Aviso "API no responde aún en :8001 (suele tardar más por torch/chromadb, mira la ventana)." }


# 11. Comprobar LM Studio (no se levanta automáticamente)
Escribe-Titulo "5. LM Studio"
$lmsOk = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:1234/v1/models" -UseBasicParsing -TimeoutSec 3
    if ($r.StatusCode -eq 200) { $lmsOk = $true }
} catch {}
if ($lmsOk) {
    Escribe-Ok "LM Studio responde en :1234. El modelo cargado debe coincidir con OPENAI_MODEL del .env."
} else {
    Escribe-Aviso "LM Studio no responde en localhost:1234."
    Write-Host ""
    Write-Host "    Pasos manuales:" -ForegroundColor White
    Write-Host "    1. Abre LM Studio." -ForegroundColor White
    Write-Host "    2. Carga el modelo (recomendado Qwen2.5-7B-Instruct-1M, Q4_K_M, 4096 tokens)." -ForegroundColor White
    Write-Host "    3. En la pestaña Developer, arranca el servidor en :1234." -ForegroundColor White
    Write-Host "    4. Asegúrate de que OPENAI_MODEL del .env coincide con el API Identifier." -ForegroundColor White
}


# 12. Abrir páginas web (siempre que la ventana correspondiente exista,
# aunque el polling no haya respondido: el navegador re-cargará si tarda).
Escribe-Titulo "6. Abriendo páginas en el navegador"
if (-not $webOk) {
    Escribe-Aviso "web_form no respondió aún, abro las URLs igualmente. Si tarda, recarga el navegador."
}
Escribe-Paso "Abriendo formulario de alta..."
Start-Process "http://localhost:8080/index.html"
Start-Sleep -Milliseconds 600
Escribe-Paso "Abriendo formulario de baja..."
Start-Process "http://localhost:8080/baja.html"
Start-Sleep -Milliseconds 600
Escribe-Paso "Abriendo formulario de actualización de stock..."
Start-Process "http://localhost:8080/ajustar_copias.html"
Start-Sleep -Milliseconds 600

if (-not $apiOk) {
    Escribe-Aviso "La API no respondió aún, abro /health igualmente. Si tarda, recarga."
}
Escribe-Paso "Abriendo /health de la API..."
Start-Process "http://localhost:8001/health"


# 13. MAUI: build + ejecutar el .exe directamente (no dotnet run).
# Motivo: el csproj tiene <TargetFrameworks> (plural). Aunque solo haya un
# framework listado, dotnet run exige --framework para resolver. Lanzar el
# .exe del bin elude todo eso y además abre la ventana de la app sin la
# consola residual de dotnet run.
Escribe-Titulo "7. Cliente MAUI"
if ($tieneDotnet) {
    $csproj = Join-Path $RAIZ "ui_maui\RpaChatApp.csproj"
    if (Test-Path $csproj) {
        Escribe-Paso "Compilando RpaChatApp (la primera vez restaura paquetes y tarda)..."
        Push-Location (Join-Path $RAIZ "ui_maui")
        try {
            & dotnet build RpaChatApp.csproj -c Debug -nologo --verbosity minimal
            if ($LASTEXITCODE -ne 0) {
                Escribe-Error "dotnet build devolvió error. Abre la solución en Visual Studio para ver el detalle."
            } else {
                Escribe-Ok "Build OK."
                # Localizo el .exe recién construido. La ruta exacta depende
                # del TargetFramework (net8.0-windows10.0.19041.0 hoy, podría
                # cambiar). Busco el más reciente bajo bin/Debug.
                $binDir = Join-Path $RAIZ "ui_maui\bin\Debug"
                $exe = Get-ChildItem -Path $binDir -Filter "RpaChatApp.exe" -Recurse -ErrorAction SilentlyContinue |
                       Sort-Object LastWriteTime -Descending |
                       Select-Object -First 1
                if ($exe) {
                    Escribe-Paso "Lanzando $($exe.Name) en ventana nueva..."
                    Start-Process -FilePath $exe.FullName -WorkingDirectory $exe.DirectoryName | Out-Null
                    Escribe-Ok "MAUI lanzado."
                } else {
                    Escribe-Aviso "No encuentro RpaChatApp.exe bajo $binDir tras el build."
                }
            }
        } finally {
            Pop-Location
        }
    } else {
        Escribe-Aviso "No encuentro $csproj."
    }
} else {
    Escribe-Aviso "Sin .NET SDK no se compila MAUI. Puedes seguir usando la CLI: python agent\app.py"
}


# 14. Resumen final
Escribe-Titulo "Demo lista"
Write-Host ""
Write-Host " Servicios:" -ForegroundColor White
Write-Host "  - web_form         http://localhost:8080/index.html" -ForegroundColor Gray
Write-Host "  - API              http://localhost:8001/health" -ForegroundColor Gray
Write-Host "  - LM Studio        http://localhost:1234/v1/models  $(if ($lmsOk) { '(OK)' } else { '(pendiente, arrancar a mano)' })" -ForegroundColor Gray
Write-Host "  - UI MAUI          ventana 'Agente RPA Chat' $(if ($tieneDotnet) { '' } else { '(no disponible: falta .NET SDK)' })" -ForegroundColor Gray
Write-Host ""
Write-Host " Páginas web abiertas para la demo:" -ForegroundColor White
Write-Host "  - Alta de libro             http://localhost:8080/index.html" -ForegroundColor Gray
Write-Host "  - Baja de libro             http://localhost:8080/baja.html" -ForegroundColor Gray
Write-Host "  - Ajuste de copias          http://localhost:8080/ajustar_copias.html" -ForegroundColor Gray
Write-Host ""
Write-Host " Si MAUI no arrancó, prueba el modo CLI:" -ForegroundColor White
Write-Host "    & '$pythonVenv' agent\app.py" -ForegroundColor Gray
Write-Host ""
Write-Host " Para parar todo: cierra cada ventana de PowerShell que se abrió." -ForegroundColor White
Write-Host ""
