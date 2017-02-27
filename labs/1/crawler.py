import scrapy


class CitySpider(scrapy.Spider):
    name = 'melkaspider'
    start_urls = ['http://127.0.0.1:8000']

    custom_settings = {
        'USER_AGENT': 'DDW',
        'DOWNLOAD_DELAY': 1.5,
        'ROBOTSTXT_OBEY': True
    }

    def parse_person(self, response):
        print('Parsing person.')
        name = response.css('span.name::text').extract()
        phone = response.css('span.phone::text').extract()
        gender = response.css('span.gender::text').extract()
        age = response.css('span.age::text').extract()

        yield {
            'name': name,
            'phone': phone,
            'gender': gender,
            'age': age,
        }

    def parse_cities(self, response):
        print("Parsing city.")
        persons = response.css('ul.persons a')
        persons_urls = persons.css('::attr(href)').extract()

        for person_url in persons_urls:
            yield scrapy.Request(response.urljoin(person_url), callback=self.parse_person)

    def parse(self, response):
        cities = response.css('ul.cities a')
        print(cities.css('::text').extract())

        cities_tocrawl = cities.css('::attr(href)').extract()

        for city_url in cities_tocrawl:
            yield scrapy.Request(response.urljoin(city_url), callback=self.parse_cities)
