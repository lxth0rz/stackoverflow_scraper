# -*- coding: utf-8 -*-
from scrapy import Spider
from urllib.parse import urljoin
from scrapy.http.request import Request


class IMDBCreatorsScraper(Spider):

    name = 'stackoverflow-users-urls'

    start_overview_url = 'https://stackoverflow.com/users?page=1&tab=reputation&filter=all'

    def start_requests(self):
        yield Request(url=self.start_overview_url,
                      callback=self.parse_overview)

    def parse_overview(self, response):

        users = response.xpath('.//div[@class="user-details"]/a/@href')
        if users and len(users) > 0:
            users = users.extract()
            users = [urljoin(response.url, x.strip()) for x in users]
            for user in users:
                print(user)

        next_url = response.xpath('.//a[@rel="next"]/@href')
        if next_url and len(next_url) > 0:
            next_url = next_url.extract()[0].strip()
            next_url = urljoin(response.url, next_url)
            yield Request(url=next_url,
                          callback=self.parse_overview)

