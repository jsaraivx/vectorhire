import os, pathlib, pymupdf

RESUME_FOLDERS = 'data/raw'

resume_files = [f for f in os.listdir(RESUME_FOLDERS) if f.endswith('.pdf')]

resume_filespath = [RESUME_FOLDERS + '/' + p for p in resume_files]

file_names = [f.strip('.pdf') for f in resume_files]

for fpath in resume_filespath:

    try:
        with pymupdf.open(fpath) as doc:  # open document
            text = chr(12).join([page.get_text() for page in doc])
        # write as a binary file to support non-ASCII characters
        pathlib.Path('data/processed/' + fpath.strip('.pdf').strip(RESUME_FOLDERS) + '.txt').write_bytes(text.encode())
        print(f'Sucessfully data processing for {fpath}')
    except Exception as e:
        print(e)
        continue
