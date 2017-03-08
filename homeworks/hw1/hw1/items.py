# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Article(scrapy.Item):
    title = scrapy.Field()
    headlines = scrapy.Field()
    content = scrapy.Field()
    paragraph_headings = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()


class Author(scrapy.Item):
    name = scrapy.Field()
