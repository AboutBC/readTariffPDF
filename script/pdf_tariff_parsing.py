# Attempt to read all of the codes from PDFs in the form xxxx.xx.xx
# Making lemonade from the repeated requests from economist on the team
#to download data, copy and paste, and simple line graphs. Citation project next probably.

import re
import requests
import pdfplumber
from pathlib import Path
import pandas as pd


# First create the names of the files, the urls to get the pdf from and the pages to limit the search.
def scrub_pdf_hts_codes():
    urls = [
        "https://ustr.gov/sites/default/files/2018-13248.pdf",
        "https://ustr.gov/sites/default/files/enforcement/301Investigations/2018-17709.pdf",
        "https://ustr.gov/sites/default/files/301/2018-0026%20China%20FRN%207-10-2018_0.pdf",
        "https://ustr.gov/sites/default/files/enforcement/301Investigations/Notice_of_Modification_%28List_4A_and_List_4B%29.pdf"
    ]
    url_names_dict = {
        "https://ustr.gov/sites/default/files/2018-13248.pdf": "list1.pdf",
        "https://ustr.gov/sites/default/files/enforcement/301Investigations/2018-17709.pdf": "list2.pdf",
        "https://ustr.gov/sites/default/files/301/2018-0026%20China%20FRN%207-10-2018_0.pdf": "list3.pdf",
        "https://ustr.gov/sites/default/files/enforcement/301Investigations/Notice_of_Modification_%28List_4A_and_List_4B%29.pdf": "list4.pdf"
    }
    # page numbers, this will stop the pdf scanner from grabbing numbers from earlier in the pdf that may be referenced as an example.
    # 0 indexed and last umber not included
    start_stop_list = [
        [4, 9, 37, 47],
        [3, 5],
        [10, 205],
        [26, 139, 146, 165]
    ]

    # establishing the text format

    hts_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')
    hts_codes_record = []

    # First we want to check if the pdf is there already. Then we want to download and save.
    loop = 0
    for url in urls:
        pdf_save_str = url_names_dict[url]
        pdf_path = Path("data") / "raw" / pdf_save_str
        if not pdf_path.exists():
            print(f"PDF {pdf_save_str} does not exist. Downloading and then scrubbing...")
            response = requests.get(url)
            with open(pdf_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"PDF {pdf_save_str} already exists. On to scrubbing...")

        # Now we scrub the pdf for the xxxx.xx.xx format but we want to limit the number of pages to the list provided above
        with pdfplumber.open(pdf_path) as pdf:
            start_stop = start_stop_list[loop]
            # defining the range fot the PDF based on the loop we are in
            length_pages = len(start_stop)
            start = start_stop[0]
            stop = start_stop[1]
            final_range = list(range(start, stop))
            if length_pages == 4:
                start_2 = start_stop[2]
                stop_2 = start_stop[3]
                second_range = list(range(start_2, stop_2))
                final_range = list(final_range + second_range)
            for page_num in final_range:
                page = pdf.pages[page_num]
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        parts = line.strip().split()
                        for part in parts:
                            if hts_pattern.match(part):
                                hts_codes_record.append({
                                    "code": part,
                                    "source": pdf_save_str
                                })
        loop += 1

    # Print Sample
    print(len(hts_codes_record))
    print("Sample HTS Code records:")
    for record in hts_codes_record[:10]:
        print(record)

    output_path = Path("data") / "processed" / "hts_codes_labeled.csv"
    print(output_path)
    pd.DataFrame(hts_codes_record).to_csv(output_path, index=False)


if __name__ == "__main__":
    scrub_pdf_hts_codes()