import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

directory = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(directory, "3-Clustering v2.pdf")
out_dir = os.path.join(directory, "pdf1_images")
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(path)
# Render all pages that had minimal text (DBSCAN, Affinity Propagation, Metrics sections)
for i in range(doc.page_count):
    page = doc[i]
    pix = page.get_pixmap(dpi=200)
    img_path = os.path.join(out_dir, f"page_{i+1:02d}.png")
    pix.save(img_path)
    print(f"Saved: page_{i+1:02d}.png")
doc.close()
print("Done!")
