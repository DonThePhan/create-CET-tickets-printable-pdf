import csv
import os

import qrcode
from qrcode.constants import ERROR_CORRECT_L
from PIL import Image

CSV_PATH = "QRs.csv"
OUTPUT_FOLDER = "qrs"

QR_SIZE = 660     # QR code itself, px
PADDING = 75      # white padding on each side, px
TOTAL_SIZE = QR_SIZE + 2 * PADDING  # 810 px


def create_qr_image(data):
    # version=None + fit=True picks the smallest QR version that holds the data
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_L,
        box_size=1,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("L")
    # Scale to exactly 660x660 regardless of module count
    img = img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)

    # Paste onto white canvas with 75px padding all around
    canvas = Image.new("L", (TOTAL_SIZE, TOTAL_SIZE), "white")
    canvas.paste(img, (PADDING, PADDING))
    return canvas


def empty_folder(folder):
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            os.remove(path)


def create_qr_pngs_from_csv(csv_path=CSV_PATH, output_folder=OUTPUT_FOLDER):
    os.makedirs(output_folder, exist_ok=True)
    empty_folder(output_folder)

    count = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            data = row["data"]
            if not name or not data:
                print(f"Skipping row with missing name/data: {row}")
                continue

            img = create_qr_image(data)
            output_path = os.path.join(output_folder, f"{name}.png")
            img.save(output_path)
            count += 1
            print(f"Created QR: {output_path}")

    print(f"Done! {count} QR(s) saved to '{output_folder}'.")


if __name__ == "__main__":
    create_qr_pngs_from_csv()
