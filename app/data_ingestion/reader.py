from PyPDF2 import PdfReader
import docx

from ..utils import  ALLOWED_EXTENSIONS


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return text

def read_txt(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def read_xlsx(file_path: str) -> str:
    df = pd.read_excel(file_path)
    return df.to_string()

def read(file_path: str) -> str:
    if file_path.endswith('.pdf'):
        return read_pdf(file_path)
    elif file_path.endswith('.docx'):
        return read_docx(file_path)
    elif file_path.endswith('.txt'):
        return read_txt(file_path)
    elif file_path.endswith('.xlsx'):
        return read_xlsx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
