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

    scrapy_by_url = scrapy_by_urls['moderators'] # default one.

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    directory_path = os.getcwd()

    filter_by = 'month'

    dataset_client = None

    def start_requests(self):

        self.logger = logging.getLogger()

        if 'upwork_2' not in self.directory_path:

            # Initialize the main ApifyClient instance
            client = ApifyClient(os.environ['APIFY_TOKEN'], api_url=os.environ['APIFY_API_BASE_URL'])

            # create a named dataset
            # dataset_collection_client = client.datasets()
            # dataset_collection_client.get_or_create(name='stackoverflow-users-urls-dataset')
            # self.dataset_client = client.dataset('MedH/stackoverflow-users-urls-dataset')

            # Get the resource subclient for working with the default key-value store of the actor
            default_kv_store_client = client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID'])

            # Get the value of the actor input and print it
            self.logger.info('Loading input...')
            actor_input = default_kv_store_client.get_record(os.environ['APIFY_INPUT_KEY'])['value']
            self.logger.info(actor_input)

            self.filter_by = actor_input["filterBy"]
            self.scrapy_by_url = self.scrapy_by_urls[actor_input["scrapeUsersBy"]]
            self.scrapy_by_url += "&filter={0}".format(self.filter_by)
            self.logger.info(self.scrapy_by_url)

        yield Request(url=self.scrapy_by_url,
                      headers=self.headers,
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
                    # client.push
                    apify.pushData(user_dict)

                    #self.dataset_client.push_items(user_dict)
                else:
                    yield user_dict

        next_url = response.xpath('.//a[@rel="next"]/@href')
        if next_url and len(next_url) > 0:
            next_url = next_url.extract()[0].strip()
            next_url = urljoin(response.url, next_url)
            yield Request(url=next_url,
                          headers=self.headers,
                          callback=self.parse_overview)

