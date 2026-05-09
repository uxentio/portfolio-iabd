"""Convierte SVG a PNG usando cairosvg."""
import subprocess, sys, os

try:
    import cairosvg
except ImportError:
    print("Instalando cairosvg...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
    import cairosvg

svg_path = sys.argv[1]
png_path = sys.argv[2]
cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1800)
print(f"OK: {png_path}")
