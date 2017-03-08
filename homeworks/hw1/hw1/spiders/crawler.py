import scrapy
from .. import items


class IhnedSpider(scrapy.Spider):
    name = 'ihned'
    start_urls = ['http://byznys.ihned.cz/dalsi-clanky/']

    scrape_pages_limit = 1

    def __init__(self):
        super().__init__()
        self.scraped_pages = 0
        self.scraped_articles = 0

    def parse_author(self, response):
        name = response.css('div.author-info a::text').extract_first()
        print("Parsing author: {}".format(name))

        info_list = response.css('div.author-info::text').extract()
        info = "; ".join([info_item.strip() for info_item in info_list if info_item.strip()])

        author = items.Author()
        author['name'] = name,
        author['info'] = info,
        author['url'] = response.url

        article = response.meta['article']
        article['author'] = author
        yield article

    def parse_article(self, response):
        title = response.css('h1::text').extract_first()
        print("Parsing article: {}".format(title))

        headlines = response.css('div.headlines ul li::text').extract()
        for headline in headlines:
            print("  - {}".format(headline))

        content = "\n".join(response.css('p.detail-odstavec::text').extract())
        if not content:
            content = "\n".join(response.css('div.article-body p::text').extract())
        print("    {}".format(content))

        paragraph_headings = response.css('h2:not(.after-arrowed)::text').extract()
        # after-arrowed is advertisement-related h2
        for heading in paragraph_headings:
            print("  \"{}\"".format(heading))

            # TODO fotogalerie vs článek

        article = items.Article()
        article['title'] = title
        article['headlines'] = headlines
        article['content'] = content
        article['paragraph_headings'] = paragraph_headings
        article['url'] = response.url

        author_url = response.css('div.article-info p.author a::attr(href)').extract_first()
        yield scrapy.Request(response.urljoin(author_url), callback=self.parse_author, meta={'article': article})

    def parse(self, response):
        if self.scraped_pages + 1 > self.scrape_pages_limit:
            print("Already scraped {} pages. {} is limit, so returning.".format(self.scraped_pages,
                                                                                self.scrape_pages_limit))
            return
        else:
            self.scraped_pages += 1

        print("Parsing article list page")
        articles_urls = response.css('div.article div.article-content a.article-more ::attr(href)').extract()

        for article_url in articles_urls:
            print(article_url)
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article)

        nextPage = scrapy.selector.HtmlXPathSelector(response).select(
            "//div[@class='content-column left']/table/tr/td[@class='norm']/a[contains(text(),'Další')]/@href").extract_first()

        print("Next page: {}".format(nextPage))
        yield scrapy.Request(response.urljoin(nextPage), callback=self.parse)
