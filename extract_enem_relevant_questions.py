from pathlib import Path
import re
import json

try:
    import pymupdf as fitz
except ImportError as exc:
    raise SystemExit('Instale o pacote pymupdf antes de executar: pip install pymupdf')

BASE_DIR = Path(r'C:\Users\flavi\OneDrive\simulacoes')
ENEM_DIR = BASE_DIR / '_shared' / 'ENEM'
OUT_DIR = BASE_DIR / '_shared' / 'ENEM' / 'extraidos'
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = [
    'lei de coulomb',
    'coulomb',
    'força elétrica',
    'forca eletrica',
    'campo elétrico',
    'campo eletrico',
    'carga elétrica',
    'carga eletrica',
    'eletrostática',
    'eletrostatica',
    'linhas de campo',
    'linhas de força',
]

QUESTION_PATTERNS = [
    re.compile(r'quest[aã]o\s*\d+', re.IGNORECASE),
    re.compile(r'quest[aã]o\s*\d+\s*\(([^)]+)\)', re.IGNORECASE),
]


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def find_question_number(text: str) -> str:
    for pattern in QUESTION_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(0)
    return 'N/A'


# busca em textos de PDF, com contexto ao redor da palavra-chave

def extract_relevant_hits(pdf_path: Path):
    doc = fitz.open(pdf_path)
    hits = []
    for page_index in range(doc.page_count):
        page = doc[page_index]
        text = page.get_text('text') or ''
        lowered = text.lower()
        for keyword in KEYWORDS:
            if keyword in lowered:
                idx = lowered.find(keyword)
                snippet = text[max(0, idx - 180): idx + 500]
                snippet = clean_text(snippet)
                hits.append({
                    'pdf': pdf_path.name,
                    'page': page_index + 1,
                    'keyword': keyword,
                    'question': find_question_number(snippet),
                    'snippet': snippet[:400],
                })
    doc.close()
    return hits


def render_page_images(pdf_path: Path, images_dir: Path):
    images_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    for page_index in range(min(doc.page_count, 8)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        out_file = images_dir / f'{pdf_path.stem}_p{page_index + 1}.png'
        pix.save(out_file)
    doc.close()
    return [str(p) for p in sorted(images_dir.glob(f'{pdf_path.stem}_p*.png'))]


all_hits = []
for pdf_file in sorted(ENEM_DIR.glob('*.pdf')):
    try:
        hits = extract_relevant_hits(pdf_file)
        if hits:
            all_hits.extend(hits)
            print(f'Arquivo: {pdf_file.name} | ocorrências: {len(hits)}')
            for hit in hits[:3]:
                print(f"  página {hit['page']} | palavra-chave: {hit['keyword']} | questão: {hit['question']}")
                print(f"  {hit['snippet'][:180]}...")
            print()
    except Exception as exc:
        print(f'Erro em {pdf_file.name}: {exc}')

out_json = OUT_DIR / 'enem_coulomb_hits.json'
out_json.write_text(json.dumps(all_hits, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nArquivo JSON salvo em: {out_json}')

# renderiza imagens das primeiras páginas para servir de inspeção visual
for pdf_file in sorted(ENEM_DIR.glob('*.pdf')):
    img_dir = OUT_DIR / pdf_file.stem
    try:
        images = render_page_images(pdf_file, img_dir)
        if images:
            print(f'Imagens salvas em: {img_dir} ({len(images)} arquivos)')
    except Exception as exc:
        print(f'Erro ao renderizar imagens de {pdf_file.name}: {exc}')
