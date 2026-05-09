"""start_demo.py — equivalente cross-platform de start_demo.ps1.

Arranca toda la demo: comprueba prerequisitos, crea venv si falta, instala
deps, indexa el RAG, levanta web_form y la API, abre las páginas del
formulario en el navegador, comprueba LM Studio (no lo arranca, no es un
servicio CLI) y lanza el cliente MAUI si hay .NET SDK.

Uso:
    python start_demo.py

Pensado para Windows, Linux y macOS. En Linux/Mac la parte de MAUI solo
funciona si hay .NET 8 SDK instalado y workload android/maui añadido; lo
habitual es saltarse esa parte fuera de Windows.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ES_WINDOWS = platform.system() == "Windows"
PY_VENV = RAIZ / (".venv/Scripts/python.exe" if ES_WINDOWS else ".venv/bin/python")


def banner(texto: str) -> None:
    print()
    print("=" * 60)
    print(texto)
    print("=" * 60)


def paso(texto: str) -> None:
    print(f"[*] {texto}")


def ok(texto: str) -> None:
    print(f"    OK {texto}")


def aviso(texto: str) -> None:
    print(f"    AVISO {texto}")


def fatal(texto: str) -> None:
    print(f"    ERROR {texto}", file=sys.stderr)
    sys.exit(1)


def comprueba_url(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return False
    except Exception:
        return False


def lanza_ventana_nueva(comando: list[str], titulo: str) -> None:
    """Abre una terminal nueva ejecutando comando. Mac y Linux abren la
    propia. En Windows se usa start con powershell."""
    if ES_WINDOWS:
        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in comando)
        subprocess.Popen(
            ["powershell", "-NoExit", "-Command", f"$Host.UI.RawUI.WindowTitle='{titulo}'; {cmd_str}"],
            cwd=str(RAIZ),
        )
    elif platform.system() == "Darwin":
        script = f'tell application "Terminal" to do script "cd \\"{RAIZ}\\" && {" ".join(comando)}"'
        subprocess.Popen(["osascript", "-e", script])
    else:
        terminales = ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"]
        terminal = next((t for t in terminales if shutil.which(t)), None)
        if terminal:
            subprocess.Popen(
                [terminal, "--", "bash", "-c", f"cd '{RAIZ}' && {' '.join(comando)}; exec bash"]
            )
        else:
            # Fallback sin terminal: lanzar en background sin ventana visible.
            subprocess.Popen(comando, cwd=str(RAIZ))


def main() -> int:
    os.chdir(RAIZ)

    # 1. Python: si ya hay venv sano, lo que importa es el python del venv,
    # no el global con el que se invocó este script.
    banner("1. Comprobando prerequisitos")
    venv_dir_tmp = RAIZ / ".venv"
    venv_sano_tmp = PY_VENV.exists() and (venv_dir_tmp / "pyvenv.cfg").exists()

    if venv_sano_tmp:
        paso("Python del venv existente (.venv)...")
        try:
            v = subprocess.check_output([str(PY_VENV), "--version"], text=True).strip()
            ok(f"{v} (del venv)")
            partes = v.replace("Python", "").strip().split(".")
            menor = int(partes[1])
            if int(partes[0]) == 3 and menor >= 14:
                aviso(f"El venv usa {v}, muy reciente. Si pip falla, recrea con:")
                aviso("  rm -rf .venv && py -3.12 -m venv .venv  (Win)")
                aviso("  rm -rf .venv && python3.12 -m venv .venv  (Linux/Mac)")
        except Exception as e:
            aviso(f"No pude consultar la versión del venv: {e}")
    else:
        paso("Python 3.11 a 3.13 (rango con wheels precompilados)...")
        py_ver = sys.version_info
        if py_ver < (3, 11):
            aviso(f"Detectado Python {py_ver.major}.{py_ver.minor}. Se recomienda 3.11+.")
        elif py_ver >= (3, 14):
            aviso(f"Python {py_ver.major}.{py_ver.minor} es muy nuevo.")
            aviso("Muchos paquetes (torch, chromadb, pydantic-core) no tienen wheels para 3.14+")
            aviso("y pip intentará compilar desde source, lo que suele fallar sin compilador.")
            aviso("Recomendado: Python 3.11, 3.12 o 3.13.")
            try:
                input("    [Enter para continuar de todos modos, Ctrl+C para abortar]")
            except KeyboardInterrupt:
                sys.exit(0)
        else:
            ok(f"Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}")

    # 2. .NET SDK (opcional)
    paso(".NET 8 SDK (opcional, para el cliente MAUI)...")
    tiene_dotnet = shutil.which("dotnet") is not None
    if tiene_dotnet:
        try:
            v = subprocess.check_output(["dotnet", "--version"], text=True).strip()
            ok(f"dotnet {v}")
        except subprocess.CalledProcessError:
            tiene_dotnet = False
            aviso("dotnet no responde correctamente.")
    else:
        aviso(".NET SDK no detectado. La UI MAUI no se podrá compilar.")

    # 3. venv con detección de venv corrupto
    banner("2. Entorno virtual y dependencias")
    venv_dir = RAIZ / ".venv"
    venv_cfg = venv_dir / "pyvenv.cfg"

    # Un venv válido tiene python ejecutable Y pyvenv.cfg. Si falta
    # cualquiera, borro y regenero: cubre el caso de un venv heredado
    # de otra ruta absoluta o uno que se quedó a medias.
    venv_sano = PY_VENV.exists() and venv_cfg.exists()
    if venv_dir.exists() and not venv_sano:
        aviso(".venv existe pero está incompleto (falta pyvenv.cfg o python). Lo recreo.")
        try:
            shutil.rmtree(venv_dir)
        except Exception as e:
            fatal(f"No pude borrar el venv corrupto: {e}")

    if not venv_dir.exists():
        paso("Creando venv en .venv...")
        r = subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=str(RAIZ))
        if r.returncode != 0:
            fatal("No pude crear el venv.")
        ok("venv creado.")
    else:
        ok("venv ya existe y está sano.")

    if not PY_VENV.exists():
        fatal(f"No encuentro {PY_VENV} tras crear el venv.")

    # 4. pip install
    # Purgo caché para evitar 'Cache entry deserialization failed' por entradas viejas.
    # --prefer-binary para que pip no compile desde source si existe wheel.
    paso("Limpiando caché de pip...")
    subprocess.run([str(PY_VENV), "-m", "pip", "cache", "purge"], capture_output=True)

    paso("Actualizando pip...")
    subprocess.run([str(PY_VENV), "-m", "pip", "install", "--upgrade", "pip",
                    "--quiet", "--no-cache-dir"])

    paso("Instalando paquetes de requirements.txt (la primera vez tarda 5-10 min)...")
    r = subprocess.run([str(PY_VENV), "-m", "pip", "install", "-r", "requirements.txt",
                        "--quiet", "--prefer-binary"])
    if r.returncode != 0:
        print("    ERROR Falló pip install. Causas habituales:", file=sys.stderr)
        print("      - Python muy nuevo (3.14+): faltan wheels precompilados.", file=sys.stderr)
        print("      - Falta compilador (Visual C++ Build Tools en Windows, gcc en Linux).", file=sys.stderr)
        print("      - Sin conexión a PyPI o proxy bloqueando.", file=sys.stderr)
        sys.exit(1)
    ok("Dependencias instaladas.")

    # 5. Playwright Chromium
    paso("Comprobando navegador de Playwright...")
    r = subprocess.run([str(PY_VENV), "-m", "playwright", "install", "chromium"])
    if r.returncode != 0:
        aviso("playwright install devolvió código no cero. Si Chromium ya estaba, ignóralo.")
    else:
        ok("Chromium listo.")

    # 6. RAG
    banner("3. Índice RAG")
    chroma = RAIZ / "rag" / ".chroma"
    if not chroma.exists():
        paso("Indexando workflows en ChromaDB (primer arranque)...")
        r = subprocess.run([str(PY_VENV), "rag/index_procedures.py"])
        if r.returncode != 0:
            fatal("Falló la indexación del RAG.")
        ok("Índice creado en rag/.chroma.")
    else:
        ok("Índice RAG ya presente. Re-indexa a mano si añades workflows.")

    # 7. .env
    env_file = RAIZ / ".env"
    if not env_file.exists():
        shutil.copy(RAIZ / ".env.example", env_file)
        aviso("Creado .env desde .env.example. Revisa OPENAI_MODEL.")

    # 8. web_form en ventana nueva
    banner("4. Levantando servidores")
    paso("Abriendo nueva ventana para el servidor web (puerto 8080)...")
    lanza_ventana_nueva([str(PY_VENV), "web_form/server.py"], titulo="web_form :8080")
    ok("web_form lanzado.")

    # 9. API en ventana nueva
    paso("Abriendo nueva ventana para la API (uvicorn, puerto 8001)...")
    lanza_ventana_nueva(
        [str(PY_VENV), "-m", "uvicorn", "agent.api:app", "--port", "8001"],
        titulo="agent api :8001",
    )
    ok("API lanzada.")

    # 10. Esperar a que respondan (90s, uvicorn tarda en cargar torch+chromadb)
    paso("Esperando a que arranquen (máx 90s)...")
    web_ok = api_ok = False
    for _ in range(45):
        time.sleep(2)
        if not web_ok:
            web_ok = comprueba_url("http://localhost:8080/index.html")
        if not api_ok:
            api_ok = comprueba_url("http://localhost:8001/health")
        if web_ok and api_ok:
            break
    if web_ok:
        ok("web_form responde en :8080.")
    else:
        aviso("web_form no responde aún en :8080 (sigue cargando, mira la ventana).")
    if api_ok:
        ok("API responde en :8001/health.")
    else:
        aviso("API no responde aún en :8001 (sigue cargando torch/chromadb, mira la ventana).")

    # 11. LM Studio
    banner("5. LM Studio")
    lms_ok = comprueba_url("http://localhost:1234/v1/models", timeout=3.0)
    if lms_ok:
        ok("LM Studio responde en :1234. El modelo cargado debe coincidir con OPENAI_MODEL del .env.")
    else:
        aviso("LM Studio no responde en localhost:1234.")
        print()
        print("    Pasos manuales:")
        print("    1. Abre LM Studio.")
        print("    2. Carga el modelo (recomendado Qwen2.5-7B-Instruct-1M, Q4_K_M, 4096 tokens).")
        print("    3. En la pestaña Developer, arranca el servidor en :1234.")
        print("    4. Asegúrate de que OPENAI_MODEL del .env coincide con el API Identifier.")

    # 12. Abrir páginas web (siempre que las ventanas existan, aunque el
    # polling no haya respondido: el navegador re-cargará si tarda).
    banner("6. Abriendo páginas en el navegador")
    if not web_ok:
        aviso("web_form no respondió aún, abro las URLs igualmente. Si tarda, recarga.")
    for url, descripcion in [
        ("http://localhost:8080/index.html", "Alta de libro"),
        ("http://localhost:8080/baja.html", "Baja de libro"),
        ("http://localhost:8080/ajustar_copias.html", "Ajuste de copias"),
    ]:
        paso(f"Abriendo {descripcion}...")
        webbrowser.open(url)
        time.sleep(0.6)
    if not api_ok:
        aviso("La API no respondió aún, abro /health igualmente. Si tarda, recarga.")
    paso("Abriendo /health de la API...")
    webbrowser.open("http://localhost:8001/health")

    # 13. MAUI: build + ejecutar el .exe directamente (no dotnet run).
    # Motivo: el csproj tiene <TargetFrameworks> (plural) y dotnet run
    # exige --framework. Lanzar el .exe del bin elude eso.
    banner("7. Cliente MAUI")
    csproj = RAIZ / "ui_maui" / "RpaChatApp.csproj"
    if tiene_dotnet and csproj.exists():
        if not ES_WINDOWS:
            aviso("MAUI con TargetFramework net8.0-windows10.x.y solo compila en Windows. Saltando.")
        else:
            paso("Compilando RpaChatApp (primera vez restaura paquetes y tarda)...")
            r = subprocess.run(
                ["dotnet", "build", "RpaChatApp.csproj", "-c", "Debug", "-nologo", "--verbosity", "minimal"],
                cwd=str(RAIZ / "ui_maui"),
            )
            if r.returncode != 0:
                aviso("dotnet build devolvió error. Abre la solución en Visual Studio para ver el detalle.")
            else:
                ok("Build OK.")
                # Localizo el .exe más reciente bajo bin/Debug.
                bin_dir = RAIZ / "ui_maui" / "bin" / "Debug"
                exes = sorted(bin_dir.rglob("RpaChatApp.exe"),
                              key=lambda p: p.stat().st_mtime, reverse=True)
                if exes:
                    paso(f"Lanzando {exes[0].name}...")
                    subprocess.Popen([str(exes[0])], cwd=str(exes[0].parent))
                    ok("MAUI lanzado.")
                else:
                    aviso(f"No encuentro RpaChatApp.exe bajo {bin_dir} tras el build.")
    else:
        if not csproj.exists():
            aviso(f"No encuentro {csproj}.")
        else:
            aviso("Sin .NET SDK no se compila MAUI. Usa la CLI: python agent/app.py")

    # 14. Resumen final
    banner("Demo lista")
    print()
    print(" Servicios:")
    print("  - web_form         http://localhost:8080/index.html")
    print("  - API              http://localhost:8001/health")
    estado_lms = "(OK)" if lms_ok else "(pendiente, arrancar a mano)"
    print(f"  - LM Studio        http://localhost:1234/v1/models  {estado_lms}")
    estado_maui = "" if tiene_dotnet else "(no disponible: falta .NET SDK)"
    print(f"  - UI MAUI          ventana 'Agente RPA Chat' {estado_maui}")
    print()
    print(" Páginas web abiertas para la demo:")
    print("  - Alta de libro             http://localhost:8080/index.html")
    print("  - Baja de libro             http://localhost:8080/baja.html")
    print("  - Ajuste de copias          http://localhost:8080/ajustar_copias.html")
    print()
    print(" Si MAUI no arrancó, prueba el modo CLI:")
    print(f"    {PY_VENV} agent/app.py")
    print()
    print(" Para parar todo: cierra cada ventana abierta.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
