import scrapy


class IhnedSpider(scrapy.Spider):
    name = 'ihned'
    start_urls = ['http://byznys.ihned.cz/dalsi-clanky/']

    def parse_author(self, response):
        name = response.css('div.author-info a::text').extract_first()
        print("Parsing author: {}".format(name))

        # TODO figure out how to output separate items in json
        yield {
            'author_name': name
        }

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

        author_name = response.css('div.article-info p.author a::text').extract_first()
        author_url = response.css('div.article-info p.author a::attr(href)').extract_first()
        print("Author url: {}".format(author_url))
        yield scrapy.Request(response.urljoin(author_url), callback=self.parse_author)

        yield {
            'title': title,
            'headlines': headlines,
            'content': content,
            'paragraph_headings': paragraph_headings,
            'author': author_name,
            'url': response.url
        }

    def parse(self, response):
        print("Parsing article list page")
        articles_urls = response.css('div.article div.article-content a.article-more ::attr(href)').extract()

        for article_url in articles_urls:
            print(article_url)
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article)
