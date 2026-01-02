import io
import PyPDF2


def extract_text_from_pdf(pdf_file):
    try:
        if hasattr(pdf_file, "getvalue"):
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
        else:
            reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_txt(txt_file):
    try:
        if hasattr(txt_file, "getvalue"):
            return txt_file.getvalue().decode("utf-8")
        with open(txt_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"TXT extraction error: {e}")
        return ""


def extract_text_from_file(file):
    name = file.name if hasattr(file, "name") else file
    ext = name.split(".")[-1].lower()

    if ext == "pdf":
        return extract_text_from_pdf(file)
    elif ext == "txt":
        return extract_text_from_txt(file)
    else:
        return ""
