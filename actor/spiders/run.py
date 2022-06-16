# -*- coding: utf-8 -*-

import os
import apify
import logging
from scrapy import Spider
from urllib.parse import urljoin
from apify_client import ApifyClient
from scrapy.http.request import Request


class IMDBCreatorsScraper(Spider):

    name = 'stackoverflow-users-urls'

    logger = None

    scrapy_by_urls = {'rep': 'https://stackoverflow.com/users?tab=reputation',
                      'new_users': 'https://stackoverflow.com/users?tab=newusers',
                      'voters': 'https://stackoverflow.com/users?tab=voters',
                      'editors': 'https://stackoverflow.com/users?tab=editors',
                      'moderators': 'https://stackoverflow.com/users?tab=moderators', }

    scrapy_by_url = scrapy_by_urls['editors']

    directory_path = os.getcwd()

    def start_requests(self):

        self.logger = logging.getLogger()

        if 'upwork_2' not in self.directory_path:

            # Initialize the main ApifyClient instance
            client = ApifyClient(os.environ['APIFY_TOKEN'], api_url=os.environ['APIFY_API_BASE_URL'])

            # Get the resource subclient for working with the default key-value store of the actor
            default_kv_store_client = client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID'])

            # Get the value of the actor input and print it
            self.logger.info('Loading input...')
            actor_input = default_kv_store_client.get_record(os.environ['APIFY_INPUT_KEY'])['value']
            self.logger.info(actor_input)

            self.scrapy_by_url = self.scrapy_by_urls[actor_input["scrapeUsersBy"]]
            self.logger.info(self.scrapy_by_url)

        yield Request(url=self.scrapy_by_url,
                      callback=self.parse_overview)

    def parse_overview(self, response):

        users = response.xpath('.//div[@class="user-details"]/a')
        if users and len(users) > 0:
            for user in users:
                user_url = urljoin(response.url, user.xpath('@href').extract()[0].strip())
                user_name = user.xpath('text()').extract()[0].strip()
                user_dict = {'Name': user_name,
                             'URL': user_url}
                
                if 'upwork_2' not in self.directory_path:
                    apify.pushData(user_dict)
                else:
                    yield user_dict

        next_url = response.xpath('.//a[@rel="next"]/@href')
        if next_url and len(next_url) > 0:
            next_url = next_url.extract()[0].strip()
            next_url = urljoin(response.url, next_url)
            yield Request(url=next_url,
                          callback=self.parse_overview)

