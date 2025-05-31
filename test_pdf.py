from fpdf import FPDF
from fpdf.enums import XPos, YPos

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)  # Arial دیگه پشتیبانی نمیشه، از Helvetica استفاده کن

pdf.cell(200, 10, text="Hello from fpdf2!", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.output("test.pdf")
