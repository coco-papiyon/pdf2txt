from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
import pdf2image

from io import StringIO
import json
import os
import sys

JSON_DIR = 'json'
IMAGE_DIR = 'image'

def get_page_text(page):
    outfp = StringIO()

    rmgr = PDFResourceManager()
    lprms = LAParams()
    device = TextConverter(rmgr, outfp, laparams=lprms) 
    iprtr = PDFPageInterpreter(rmgr, device)
    iprtr.process_page(page)

    text = outfp.getvalue()
    outfp.close()
    device.close()

    return text

check_words = []
check_words.append('January')
check_words.append('Maine')
check_words.append('Augusta')
check_words.append('State')
check_words.append('Synopsis')
check_words.append('Michaud')

def is_newline(i, lines):
    line = lines[i]
    
    next_line = ""
    if i < len(lines) - 1:
        next_line = lines[i+1].strip()

    last_char = ""
    next_char = ""
    next_word = line.split(' ')[0].replace('.', '').replace(',', '')

    if len(line) > 0:
        last_char = line[len(line) - 1]
    if len(next_line) > 0:
        next_char = next_line[0]

    #if next_word in check_words:
    #    return False
    
    if next_char.isupper():
        return True
    if last_char == ".":
        return True
    if next_char == '•':
        return True
    if next_char == '▪':
        return True
    if next_char == '':
        return True

    return False
    
def convert(file):
    data = []
    with open(file, 'rb') as f:

        prev_line = ''
        for page_num, page in enumerate(PDFPage.get_pages(f)):
            page_data = {}
            page_data['page'] = page_num
            page_data['line'] = []
            page_data['count'] = 0
            data.append(page_data)
            text = get_page_text(page)

            lines = text.split('\n')
            
            for i in range(len(lines)):
                line = lines[i]
                line = line.strip()

                if is_newline(i, lines):
                    if prev_line + line != '':
                        page_data['line'].append(prev_line + line)
                        page_data['count'] = len(page_data['line'])
                        #data[page_num].append(prev_line + line)

                    prev_line = ''
                else:
                    prev_line = prev_line + line + " "

            
            #if page_num == 1:
            #    for line in new_line:
            #        print("-----")
            #        print(line)
            #    break

    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    filename = os.path.splitext(os.path.basename(file))[0]
    filename = filename.replace(' ', '_')

    outfile = os.path.join(JSON_DIR, filename + '.json')
    with open(outfile, 'w') as f:
        json.dump(data, f, indent=2)

    images = pdf2image.convert_from_path(file, dpi=200, fmt='jpg', poppler_path=r'D:\app\poppler-23.11.0\Library\bin')
    for i, image in enumerate(images):
        outfile = os.path.join(IMAGE_DIR, filename + "_" + str(i) + '.jpg')
        image.save(outfile)
                      
if __name__ == "__main__":
    if len(sys.argv) > 0:
        convert(sys.argv[1])
    else:
        convert("pdf\Water Management by Local Governments.pdf")
