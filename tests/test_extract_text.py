import io
from PyPDF2 import PdfWriter
from PyPDF2.generic import NameObject, DictionaryObject, NumberObject, StreamObject
from asset_app import extract_text_from_pdf

def create_pdf(text: str) -> io.BytesIO:
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)

    # Define a simple Helvetica font
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
    })

    # Create content stream with the provided text
    content = f"BT /F1 12 Tf 50 150 Td ({text}) Tj ET"
    stream = StreamObject()
    stream._data = content.encode("latin-1")
    stream[NameObject("/Length")] = NumberObject(len(stream._data))
    stream_ref = writer._add_object(stream)
    page[NameObject("/Contents")] = stream_ref

    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

def test_extract_text_from_pdf():
    expected = "Hello Test"
    pdf_file = create_pdf(expected)
    result = extract_text_from_pdf(pdf_file)
    assert result.strip() == expected
