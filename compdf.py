import os
import sys
import argparse
from PIL import Image
from pypdf import PdfReader, PdfWriter

def compress_pdf(input_path: str, output_path: str = None, quality: int = 50, scale: float = 1.0):
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        # Compress page content streams
        page.compress_content_streams()

        # Compress and optionally downscale embedded images
        for img in page.images:
            try:
                pil_img = img.image
                if scale < 1.0:
                    new_w = max(1, int(pil_img.width * scale))
                    new_h = max(1, int(pil_img.height * scale))
                    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Convert palette/alpha modes if needed for JPEG compression inside PDF
                if pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")

                img.replace(pil_img, quality=quality)
            except Exception:
                pass

    writer.compress_identical_objects()

    with open(output_path, "wb") as f:
        writer.write(f)

    size_before = os.path.getsize(input_path)
    size_after = os.path.getsize(output_path)
    saved = (1 - (size_after / size_before)) * 100

    print("\n--- Compression Result ---")
    print(f"Input   : {input_path} ({size_before / 1024:.1f} KB)")
    print(f"Output  : {output_path} ({size_after / 1024:.1f} KB)")
    print(f"Reduced : {saved:.1f}%")

def main():
    parser = argparse.ArgumentParser(description="Simple PDF Compressor without venv.")
    parser.add_argument("input", nargs="?", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Path to output PDF file (optional)")
    parser.add_argument("-q", "--quality", type=int, default=50, help="Image quality 1-100 (default: 50, lower = smaller file)")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="Image resolution scale 0.1-1.0 (default: 1.0, e.g. 0.7)")

    args = parser.parse_args()

    # Interactive mode if run without CLI arguments
    if not args.input:
        input_pdf = input("Input PDF file path: ").strip().strip('"').strip("'")
        if not input_pdf:
            print("No file provided. Exiting.")
            sys.exit(0)
        out_pdf = input("Output PDF file path (Enter to auto-name): ").strip().strip('"').strip("'") or None
        q_val = input("Image quality (1-100, default 50): ").strip()
        s_val = input("Image scale (0.1-1.0, default 1.0): ").strip()

        quality = int(q_val) if q_val else 50
        scale = float(s_val) if s_val else 1.0
        compress_pdf(input_pdf, out_pdf, quality=quality, scale=scale)
    else:
        compress_pdf(args.input, args.output, quality=args.quality, scale=args.scale)

if __name__ == "__main__":
    main()
