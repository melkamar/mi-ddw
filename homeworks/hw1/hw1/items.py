# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExtendableItem(scrapy.Item):
    def __setitem__(self, key, value):
        self._values[key] = value
        self.fields[key] = {}


class Article(ExtendableItem):
    title = scrapy.Field()
    headlines = scrapy.Field()
    content = scrapy.Field()
    paragraph_headings = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()


class Photogallery(ExtendableItem):
    title = scrapy.Field()
    photos = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()


class Photo(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()


class Author(scrapy.Item):
    name = scrapy.Field()
    info = scrapy.Field()
    url = scrapy.Field()
