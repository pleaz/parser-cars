# -*- coding: utf-8 -*-

from usedcars.items import DealerItem
import scrapy
import re


class DealersSpider(scrapy.Spider):
    name = 'dealers'
    allowed_domains = ['usedcarsni.com']
    start_urls = ['https://www.usedcarsni.com/search_results.php?search_type=15&dcat[]=1&pagepc0=1']

    def parse(self, response):
        links = response.xpath('//div[@class="car-list"]//div[@class="user-description"]//a')
        for link in links:
            dealer_url = link.xpath('@href').extract_first().strip()
            yield scrapy.Request(response.urljoin(dealer_url), callback=self.parse_dealer)

        next_page = response.xpath('//ul[contains(@class, "pagination")]//a[contains(text(), "Next")]/@href').\
            extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page))

    @staticmethod
    def parse_dealer(response):
        exist = response.xpath(
            '//a[contains(@href, "https://www.usedcarsni.com/used-cars/dealers")]//text()[normalize-space()]'
        ).extract_first()
        if exist:
            cars = int(re.search(r'(\d+)', exist).group())
            if cars:
                item = DealerItem()
                title = response.xpath('//h1[not(@id) and not(@class)]/text()').extract_first()
                if title:
                    item['name'] = title.strip()
                item['url'] = response.url.replace('https://www.usedcarsni.com', '')
                item['cars'] = cars
                yield item
