import requests
from bs4 import BeautifulSoup


def crawler(seed):
    frontier = [seed]
    crawled = []
    while frontier:
        page = frontier.pop()
        try:
            print('Crawled:' + page)
            source = requests.get(page).text
            soup = BeautifulSoup(source, "html5lib")
            links = soup.findAll('a', href=True)

            if page not in crawled:
                for link in links:
                    frontier.append(link['href'])
                crawled.append(page)

        except Exception as e:
            print(e)
    return crawled


crawler('https://fit.cvut.cz')
