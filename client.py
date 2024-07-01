import requests
import json
import os
from datetime import datetime

url = 'http://localhost:5000/extract_text'

# Choose your PDF file path
# pdf_file_path = 'data/large_example.pdf'
# pdf_file_path = 'data/small_example.pdf'
pdf_file_path = 'data/medium_example.pdf'

pdf_file_name = os.path.basename(pdf_file_path)

log_file_name = f'dataout/{pdf_file_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_log.txt'

start_time = datetime.now()

with open(pdf_file_path, 'rb') as pdf_file:
    files = {'file': (pdf_file_name, pdf_file, 'application/pdf')}
    response = requests.post(url, files=files)

end_time_receive = datetime.now()

if response.status_code == 200:
    extracted_texts = response.json().get('texts', [])

    start_time_format = datetime.now()
    pages = {f"page{i+1}": text.strip() for i, text in enumerate(extracted_texts)}
    end_time_format = datetime.now()

    output_file_path = f'dataout/{os.path.splitext(pdf_file_name)[0]}_extracted_texts_pages.json'
    with open(output_file_path, 'w') as outfile:
        json.dump(pages, outfile, indent=4)

    with open(log_file_name, 'w') as log_file:
        log_file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"PDF file: {pdf_file_path}\n")
        log_file.write(f"Time to receive response: {end_time_receive - start_time}\n")
        log_file.write(f"Time to format texts: {end_time_format - start_time_format}\n")
        log_file.write(f"Extracted texts saved to {output_file_path}\n")

    print(f"Extracted texts saved to {output_file_path}")
    print(f"Log file saved to {log_file_name}")
else:
    print(f"Error: {response.status_code} - {response.json().get('error')}")
