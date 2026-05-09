"""Mapea las ejecuciones de RPA registradas en `data/rpa_ejecucion.log`
contra el archivo de vídeo de OBS, para saber a qué `mm:ss` del vídeo hay
que insertar cada `.webm` grabado por Playwright.

Uso:
    python tests/mapear_rpa_al_video.py RUTA_VIDEO_OBS [--inicio HH:MM:SS]

Si no se pasa --inicio, intenta deducir la hora de inicio de la grabación
a partir de la fecha de creación del fichero. En NTFS Windows funciona
bien; si el editor lo ha re-guardado, conviene pasar --inicio a mano.

Ejemplo:
    python tests/mapear_rpa_al_video.py ~/Videos/demo.mkv
    python tests/mapear_rpa_al_video.py ~/Videos/demo.mkv --inicio 14:30:00
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, time as dtime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "data" / "rpa_ejecucion.log"
VIDEOS_DIR = ROOT / "data" / "videos"


# Formato del logger del runner: "2026-05-07 14:32:15,429 [INFO] INICIO: workflow alta_libro"
_TS_RE = re.compile(
    r"^(?P<fecha>\d{4}-\d{2}-\d{2}) (?P<hora>\d{2}:\d{2}:\d{2}),\d+ "
    r"\[(?P<lvl>\w+)\] (?P<msg>.*)$"
)
_INICIO_RE = re.compile(r"INICIO: workflow (\S+)")
_FIN_RE = re.compile(r"FIN: workflow (\S+) (OK|KO|FAIL)")


def parsear_log(path: Path) -> list[dict]:
    """Devuelve una lista de dicts con {workflow, inicio, fin, duracion_s, ok}.
    Empareja cada INICIO con su FIN posterior."""
    if not path.exists():
        return []
    abiertas: dict[str, datetime] = {}
    cerradas: list[dict] = []
    for linea in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _TS_RE.match(linea)
        if not m:
            continue
        ts = datetime.strptime(f"{m['fecha']} {m['hora']}", "%Y-%m-%d %H:%M:%S")
        msg = m["msg"]
        m_ini = _INICIO_RE.search(msg)
        if m_ini:
            abiertas[m_ini.group(1)] = ts
            continue
        m_fin = _FIN_RE.search(msg)
        if m_fin:
            wf = m_fin.group(1)
            estado = m_fin.group(2)
            ini = abiertas.pop(wf, None)
            if ini is None:
                continue
            cerradas.append({
                "workflow": wf,
                "inicio": ini,
                "fin": ts,
                "duracion_s": int((ts - ini).total_seconds()),
                "ok": estado == "OK",
            })
    return cerradas


def localizar_webm(workflow: str, inicio: datetime) -> Path | None:
    """Busca en `data/videos/` un .webm cuyo nombre contenga el workflow y
    una hora cercana al inicio del log (margen ±90 s). Si Playwright usa
    otro patrón de nombre, devuelve None."""
    if not VIDEOS_DIR.exists():
        return None
    candidatos = sorted(VIDEOS_DIR.glob(f"{workflow}*.webm"))
    if not candidatos:
        # Algunas versiones de Playwright nombran los videos como hashes;
        # en ese caso devolver el más cercano por mtime.
        candidatos = sorted(VIDEOS_DIR.glob("*.webm"), key=lambda p: p.stat().st_mtime)
    if not candidatos:
        return None
    # Quédate con el que tenga mtime más cercano al inicio.
    target = inicio.timestamp()
    candidatos.sort(key=lambda p: abs(p.stat().st_mtime - target))
    return candidatos[0]


def parsear_inicio(arg: str | None, video: Path) -> datetime:
    """Resuelve la hora de inicio del vídeo OBS. Si --inicio viene como
    HH:MM:SS, combina con la fecha del fichero. Si no, tira de mtime."""
    fecha_video = datetime.fromtimestamp(video.stat().st_mtime)
    if not arg:
        # Intento usar ctime; en Windows suele equivaler a "fecha de creación".
        try:
            ctime = video.stat().st_ctime
            fecha_video = datetime.fromtimestamp(ctime)
        except Exception:
            pass
        return fecha_video
    try:
        h = dtime.fromisoformat(arg)
    except ValueError:
        print(f"--inicio inválido: {arg!r}. Usa HH:MM:SS.", file=sys.stderr)
        sys.exit(2)
    return datetime.combine(fecha_video.date(), h)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path, help="Ruta al .mkv/.mp4 grabado por OBS.")
    parser.add_argument("--inicio", default=None, help="Hora exacta de inicio del vídeo (HH:MM:SS).")
    parser.add_argument("--log", default=LOG_FILE, type=Path, help=f"Ruta al log del runner (default: {LOG_FILE}).")
    args = parser.parse_args(argv)

    if not args.video.exists():
        print(f"No encuentro el vídeo: {args.video}", file=sys.stderr)
        return 1

    inicio_video = parsear_inicio(args.inicio, args.video)
    ejecuciones = parsear_log(args.log)
    if not ejecuciones:
        print(f"No hay ejecuciones registradas en {args.log}.")
        print("Arranca al menos un workflow con el agente y vuelve a ejecutar este script.")
        return 0

    print(f"Vídeo OBS:       {args.video}")
    print(f"Inicio asumido:  {inicio_video.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log del runner:  {args.log}")
    print(f"Ejecuciones:     {len(ejecuciones)}")
    print("─" * 92)
    print(f"{'Workflow':22s}  {'mm:ss inicio':>12s}  {'mm:ss fin':>10s}  {'dur':>5s}  {'estado':>6s}  .webm")
    print("─" * 92)

    for ej in ejecuciones:
        offset_ini = (ej["inicio"] - inicio_video).total_seconds()
        offset_fin = (ej["fin"] - inicio_video).total_seconds()
        if offset_ini < 0:
            # Ejecución anterior al vídeo: o bien --inicio mal puesto,
            # o el log tenía runs viejos. Aviso pero sigo.
            mm_ss_ini = f"-{abs(int(offset_ini))//60:02d}:{abs(int(offset_ini))%60:02d}"
            mm_ss_fin = "—"
        else:
            mm_ss_ini = f"{int(offset_ini)//60:02d}:{int(offset_ini)%60:02d}"
            mm_ss_fin = f"{int(offset_fin)//60:02d}:{int(offset_fin)%60:02d}"
        webm = localizar_webm(ej["workflow"], ej["inicio"])
        ruta_webm = webm.relative_to(ROOT) if webm else "(no encontrado)"
        estado = "OK" if ej["ok"] else "FAIL"
        print(f"{ej['workflow']:22s}  {mm_ss_ini:>12s}  {mm_ss_fin:>10s}  {ej['duracion_s']:>3d} s  {estado:>6s}  {ruta_webm}")

    print("─" * 92)
    print()
    print("Cómo usar esto en Clipchamp:")
    print("  1. Importa el vídeo OBS y arrástralo a la pista 1.")
    print("  2. Importa los .webm de la columna y arrástralos a la pista 2 (encima).")
    print("  3. Coloca cada .webm justo en el 'mm:ss inicio' indicado.")
    print("  4. Recórtalo a la duración indicada (o un poco más para que se vea el final).")
    print("  5. Si quieres pantalla completa: maximiza el .webm. Si quieres PiP:")
    print("     redúcelo a una esquina y deja la consola del agente debajo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
