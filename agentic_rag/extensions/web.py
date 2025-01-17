import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
DDGS_MAX_RESULTS_THRESHOLD = 5

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def search_duckduckgo(query: str):
    results = list(DDGS().text(query, max_results=DDGS_MAX_RESULTS_THRESHOLD))
    if results:
        response = requests.get(results[2]['href'], headers=headers)
        print(results[0]['href'])
        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, "html.parser")

            text = ""

            elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
            for element in elements:
                text += element.get_text() + "\n"
                print(element)

    return "NOT_SCRAPABLE"


print(search_duckduckgo("what does professor shaifu gupta specialize in within the field of computer science"))
