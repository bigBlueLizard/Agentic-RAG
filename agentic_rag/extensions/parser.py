import os
import json
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from constants import CSV_FOLDER, DATA_FOLDER, CLEANED_DATA_FOLDER, TABLE_KEY, TABLE_SYNTAX, UNSTRUCTURED_API_KEY, UNSTRUCTURED_API_URL
from bs4 import BeautifulSoup
import csv

def html_table_to_csv(html_content: str, csv_filename: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in table.find_all('tr'):
            columns = row.find_all(['td', 'th'])
            row_data = [col.get_text(strip=True) for col in columns]
            writer.writerow(row_data)


def parse_file(file_name: str) -> None:
    """
    Element type	    Description
    `NarrativeText`	    NarrativeText is an element consisting of multiple, well-formulated sentences. This excludes elements such titles, headers, footers, and captions.

    `Formula`	        An element containing formulas in a document.

    `FigureCaption`	    An element for capturing text associated with figure captions.

    `ListItem`	        ListItem is a NarrativeText element that is part of a list.

    `Title`	            A text element for capturing titles.

    `Address`	        A text element for capturing physical addresses.

    `EmailAddress`	    A text element for capturing email addresses.

    `Image`	            A text element for capturing image metadata.

    `PageBreak`	        An element for capturing page breaks.

    `Table`	            An element for capturing tables.

    `Header`	        An element for capturing document headers.

    `Footer`	        An element for capturing document footers.

    `CodeSnippet`	    An element for capturing code snippets.

    `PageNumber`	    An element for capturing page numbers.

    `UncategorizedText`	Base element for capturing free text from within document.

    """
    Pipeline.from_configs(
            context=ProcessorConfig(),
            indexer_config=LocalIndexerConfig(input_path=f"./{DATA_FOLDER}/{file_name}"),
            downloader_config=LocalDownloaderConfig(),
            source_connection_config=LocalConnectionConfig(),
            partitioner_config=PartitionerConfig(
                partition_by_api=True,
                api_key=UNSTRUCTURED_API_KEY,
                partition_endpoint=UNSTRUCTURED_API_URL,
                strategy="hi_res",
                additional_partition_args={
                    "split_pdf_page": True,
                    "split_pdf_allow_failed": True,
                    "split_pdf_concurrency_level": 15,
                    "extract_images_in_pdf": True,
                    "extract_image_block_types": ["Image"],
                    "extract_image_block_to_payload":True
                },
            ),
            uploader_config=LocalUploaderConfig(output_dir=f"./{CLEANED_DATA_FOLDER}")
        ).run()
    #TODO: add drive uploader config

    final_content = ""
    with open(f"./{CLEANED_DATA_FOLDER}/{file_name}.json", "r") as f:
        data = json.load(f)
        for element in data:
            if element['type'] == 'Table':
                html_table_to_csv(element['metadata']['text_as_html'], csv_filename=f"./{CSV_FOLDER}/{element['element_id']}.csv")
                final_content += TABLE_SYNTAX.replace(TABLE_KEY, element['element_id'] + ".csv") + "\n"
            elif element['type'] in ['NarrativeText', 'UncategorizedText', 'Title']:
                final_content += element['text'] + "\n"
    return final_content
