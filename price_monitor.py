import scrapy
import json
from urllib.parse import urljoin

item_set = set()

class PriceMonitorSpider(scrapy.Spider):
    name = "price_monitor"
    CSV_FILE = 'backcountry.csv'

    custom_settings = {
        #without defining a user agent the scrapy spider gets flagged as a bot and reponse is error 403
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        },
        #define parameters for csv output
        'FEEDS': {
            CSV_FILE: {
                'format': 'csv',
                'encoding': 'utf-8',
                'overwrite': True
            },
        }
    }

    #get keyword arg list passed from scheduler
    def __init__(self, keywords=None, **kwargs):
        #this array should be of size 1 for the file naming conventions and search term
        # concatenation to work as intended
        self.start_urls = ['https://www.backcountry.com/Store/catalog/search.jsp?q=']
    
        self.CSV_FILE = 'backcountry_'
        self.keywords = keywords

        ctr = 0
        for k in self.keywords:
            ctr += 1
            self.CSV_FILE += k
            self.start_urls[0] += k
            if ctr != len(self.keywords):
                self.CSV_FILE += '_'
                self.start_urls[0] += '+'
        self.CSV_FILE += '.csv'

        super().__init__(**kwargs)

        print(self.start_urls[0])

    def parse(self, response):
        #get all product links from search page and build full url
        listing_links = response.css('a.chakra-linkbox__overlay::attr(href)').getall()
        listing_urls = [urljoin(response.url, link) for link in listing_links]
        
        #calls parse_listing for each url
        for url in listing_urls:
            yield scrapy.Request(url=url, callback=self.parse_listing)
        
        #check if additional page of results
        next_page = response.css('a[aria-label="Next page"]::attr(href)').get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_listing(self, response):
        #access link
        json_data = json.loads(response.xpath('//script[@type="application/ld+json"]/text()')[1].get())

        #create item for each variant
        for listing in json_data['hasVariant']:
            in_stock = False
            if 'InStock' in listing['offers']['availability']: in_stock = True
            item = {
                'brand' : json_data['brand']['name'],
                'product' : listing['name'],
                'color': listing['color'],
                'instock': in_stock,
                'price': listing['offers']['price'],
                'url': response.url
            }

            #handle duplicates prior to yielding item
            id_str = item['product'] + item['color']
            if id_str not in item_set:
                item_set.add(id_str)
                yield(item)
