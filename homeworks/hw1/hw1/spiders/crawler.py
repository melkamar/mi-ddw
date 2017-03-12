import scrapy
from .. import items


class IhnedSpider(scrapy.Spider):
    name = 'ihned'
    start_urls = ['http://byznys.ihned.cz/dalsi-clanky/']

    scrape_pages_limit = 25

    def __init__(self):
        super().__init__()
        self.scraped_pages = 0
        self.scraped_articles = 0
        self.authors = {}

    def get_author_info(self, response):
        name = response.css('div.article-info p.author a::text').extract_first()
        print("Parsing author: {}".format(name))

        info_list = response.css('div.article-info p.author::text').extract()
        info = "; ".join([info_item.strip() for info_item in info_list if info_item.strip()])

        author = items.Author()
        author['name'] = name,
        author['info'] = info,
        author['url'] = response.url

        print("Parsed author: {}".format(name))
        print(author)

        return author

    def parse_article(self, response):
        print("parse_article {}".format(response.url))
        title = response.css('h1::text').extract_first()
        print("Parsing article: {}".format(title))

        article_label = response.css('div.tag-list span.label::text').extract_first()
        if article_label and article_label.lower() == 'fotogalerie':
            article = items.Photogallery()
            article['photos'] = []
            pics = response.css('div#content.main-container div.main.wrapper.clearfix script::text').re_first(
                r'var\s+iobjects\s*=\s*([^;]*}\s*)\s*;')

            import json
            pics = json.loads(pics)

            print(pics.keys())
            for pic in pics[list(pics.keys())[0]]['items']:
                photo = items.Photo()
                photo['url'] = pic['large_image']['url']
                photo['name'] = pic['name']
                article['photos'].append(photo)
        else:
            headlines = response.css('div.headlines ul li::text').extract()
            for headline in headlines:
                print("  - {}".format(headline))

            content = "\n".join(response.css('p.detail-odstavec::text').extract())
            if not content:
                content = "\n".join(response.css('div.article-body p::text').extract())
            print("    {}".format(content))

            paragraph_headings = response.css('div.article-body h2:not(.after-arrowed)::text').extract()
            # after-arrowed is advertisement-related h2
            for heading in paragraph_headings:
                print("  \"{}\"".format(heading))

            article = items.Article()
            article['headlines'] = headlines
            article['content'] = content
            article['paragraph_headings'] = paragraph_headings

        article['url'] = response.url
        article['title'] = title

        article['author'] = self.get_author_info(response)
        yield article

    def parse(self, response):
        # yield scrapy.Request(response.url, callback=self.parse_article)
        # return

        if self.scraped_pages + 1 > self.scrape_pages_limit:
            print("Already scraped {} pages. {} is limit, so returning.".format(self.scraped_pages,
                                                                                self.scrape_pages_limit))
            return
        else:
            self.scraped_pages += 1

        print("Parsing article list page at {}".format(response.url))
        articles_urls = response.css('div.article div.article-content a.article-more::attr(href)').extract()

        for article_url in articles_urls:
            print(article_url)
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article)

        nextPage = scrapy.selector.HtmlXPathSelector(response).select(
            "//div[@class='content-column left']/table/tr/td[@class='norm']/a[contains(text(),'Další')]/@href").extract_first()

        print("Next page: {}".format(nextPage))
        yield scrapy.Request(response.urljoin(nextPage), callback=self.parse)
