import os
import time

from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

from create_qrs_from_csv import create_qr_pngs_from_csv


# Example trimming function
def trim_qr(qr_path, trim_pixels=75):
    img = Image.open(qr_path)
    width, height = img.size

    # Calculate new bounding box
    left = trim_pixels
    top = trim_pixels
    right = width - trim_pixels
    bottom = height - trim_pixels

    # Crop the image
    img_cropped = img.crop((left, top, right, bottom))
    return img_cropped

# Paths
TEMPLATE_PATH = "cet_printable_template.pdf"
QR_FOLDER = "qrs"
OUTPUT_FOLDER = "generated_tickets"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

DPI = 72

# Card dimensions in points
CARD_WIDTH = 2 * DPI  # 252pt
CARD_HEIGHT = 3.5 * DPI   # 144pt

# QR code size and position (points)
QR_SIZE = 1.17 * DPI    # 83.5pt
QR_X = (CARD_WIDTH - QR_SIZE) / 2  # center horizontally
QR_Y = CARD_HEIGHT - QR_SIZE - 1/6 * DPI # 10pt margin from top

def empty_folder(folder):
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            os.remove(path)


def create_ticket_pdfs_from_qr_pngs():
    empty_folder(OUTPUT_FOLDER)
    for qr_file in os.listdir(QR_FOLDER):
        if qr_file.endswith(".png"):
            ticket_number = os.path.splitext(qr_file)[0]
            qr_path = os.path.join(QR_FOLDER, qr_file)
            trimmed_qr = trim_qr(qr_path)

            # Create temporary PDF for QR
            tmp_pdf_path = f"tmp_{ticket_number}.pdf"
            c = canvas.Canvas(tmp_pdf_path, pagesize=(CARD_WIDTH, CARD_HEIGHT))
            c.drawImage(ImageReader(trimmed_qr), QR_X, QR_Y, QR_SIZE, QR_SIZE)
            c.setFont("Helvetica-Bold", 9.6)
            c.drawString(CARD_WIDTH / 2 + 8, CARD_HEIGHT / 2 - 16.5, str(ticket_number))
            c.save()

            # Load a fresh template for this ticket
            template_pdf = PdfReader(TEMPLATE_PATH)  # << reload template each iteration
            template_page = template_pdf.pages[0]
            qr_pdf = PdfReader(tmp_pdf_path)
            template_page.merge_page(qr_pdf.pages[0])
            os.remove(tmp_pdf_path)

            # Save final ticket
            output_path = os.path.join(OUTPUT_FOLDER, f"{ticket_number}.pdf")
            writer = PdfWriter()
            writer.add_page(template_page)
            with open(output_path, "wb") as f:
                writer.write(f)

            print(f"Generated ticket: {ticket_number}")
    print("All tickets generated!")

def consolidate_pdfs():
    output_pdf = "cet_printable_tickets.pdf"

    # Get all PDF files in the folder and sort them alphabetically
    pdf_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.lower().endswith(".pdf")]
    pdf_files.sort(key=lambda x: int(x.replace('.pdf', '')))

    merger = PdfMerger()

    for pdf_file in pdf_files:
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_file)
        merger.append(pdf_path)

    with open(output_pdf, "wb") as f_out:
        merger.write(f_out)

    merger.close()

    print(f"Combined PDF created: {output_pdf}")

create_qr_pngs_from_csv()
create_ticket_pdfs_from_qr_pngs()
consolidate_pdfs()
