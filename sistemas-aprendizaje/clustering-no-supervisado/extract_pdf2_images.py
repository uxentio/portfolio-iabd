import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

directory = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(directory, "Presentación_clustering_afinidad.pdf")
out_dir = os.path.join(directory, "pdf2_images")
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(path)
for i in range(doc.page_count):
    page = doc[i]
    # Render page as image at 200 DPI
    pix = page.get_pixmap(dpi=200)
    img_path = os.path.join(out_dir, f"page_{i+1:02d}.png")
    pix.save(img_path)
    print(f"Saved: {img_path}")
doc.close()
print("Done!")
