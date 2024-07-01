import os
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
import pytesseract
import cv2
import tempfile
import concurrent.futures

app = Flask(__name__)

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, 300) 
    temp_files = []
    for i, image in enumerate(images):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        image.save(temp_file.name, 'JPEG')
        temp_files.append(temp_file.name)
    return temp_files

def extract_text_from_images(image_files):
    texts = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, image_file) for image_file in image_files]
        for future in concurrent.futures.as_completed(futures):
            texts.append(future.result())
    return texts

def process_image(image_file):
    image = cv2.imread(image_file)
    text = pytesseract.image_to_string(image)
    return text

def cleanup_temp_files(temp_files):
    for temp_file in temp_files:
        os.remove(temp_file)

@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.pdf'):
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        file.save(temp_pdf.name)
        temp_files = pdf_to_images(temp_pdf.name)
        
        extracted_texts = extract_text_from_images(temp_files)
        cleanup_temp_files(temp_files)
        
        temp_pdf.close()
        os.remove(temp_pdf.name)
        
        return jsonify({'texts': extracted_texts})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)

