import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import fitz

directory = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(directory, "Presentación_clustering_afinidad.pdf")
doc = fitz.open(path)
print(f'Total pages: {doc.page_count}')
for i in range(doc.page_count):
    page = doc[i]
    text = page.get_text()
    images = page.get_images()
    print(f'\nPAGE {i+1}: text_len={len(text.strip())}, images={len(images)}')
    if text.strip():
        print(f'TEXT: {text[:500]}')
    # Also try getting text with different options
    text2 = page.get_text("text")
    text3 = page.get_text("blocks")
    if not text.strip():
        print(f'  blocks: {text3[:500] if text3 else "empty"}')
doc.close()
