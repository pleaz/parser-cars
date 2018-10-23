# -*- coding: utf-8 -*-

from usedcar.items import CarItem
import scrapy
import json
import re


class CarsSpider(scrapy.Spider):
    name = 'cars'
    allowed_domains = ['usedcarsni.com']
    start_urls = ['https://www.usedcarsni.com/directory/Used-Audi-NI']

    def parse(self, response):
        catalog_url = response.xpath('//a[contains(@title, "View All Seller\'s cars")]/@href').extract_first()
        if catalog_url:
            yield scrapy.Request(catalog_url, callback=self.parse_cars)

    def parse_cars(self, response):
        car_urls = response.xpath('//div[@class="car-list"]//div[@class="car-description"]//a/@href').extract()
        for car_url in car_urls:
            yield scrapy.Request(response.urljoin(car_url), callback=self.parse_car)

        next_page = response.xpath('//ul[contains(@class, "pagination")]//a[contains(text(), "Next")]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse_cars)

    def parse_car(self, response):
        item = CarItem()

        item['id'] = response.xpath('//a[@title="Print Advert"]/@href').extract_first().replace('/print_flyer.php?CarId=', '')
        item['condition'] = 'Used'
        item['variant'] = '0'

        make_list = {'137': 'Abarth', '5': 'Alfa Romeo', '219856463': 'Alpine', '70': 'Aston Martin', '1': 'Audi', '54': 'Austin', '46': 'Bentley', '2': 'BMW', '42': 'Chevrolet', '3': 'Chrysler', '4': 'Citroen', '792': 'Corvette', '793': 'Dacia', '58': 'Daf', '34': 'Daihatsu', '48': 'Dodge', '170978731': 'DS', '43': 'Ferrari', '6': 'Fiat', '7': 'Ford', '116307351': 'Great Wall', '8': 'Honda', '9': 'Hyundai', '799': 'Infiniti', '10': 'Isuzu', '37': 'Iveco', '11': 'Jaguar', '12': 'Jeep', '13': 'Kia', '65': 'Lamborghini', '14': 'Land Rover', '36': 'Lexus', '52': 'Lotus', '51': 'Maserati', '15': 'Mazda', '16': 'Mercedes', '17': 'MG', '18': 'MINI', '19': 'Mitsubishi', '56': 'Morris', '20': 'Nissan', '22': 'Peugeot', '23': 'Porsche', '38': 'Proton', '24': 'Renault', '25': 'Rover', '26': 'SAAB', '27': 'Seat', '28': 'Skoda', '47': 'Smart', '41': 'SsangYong', '40': 'Subaru', '29': 'Suzuki', '30': 'Toyota', '50': 'TVR', '31': 'Vauxhall', '32': 'Volkswagen', '33': 'Volvo'}
        title = response.xpath('//h1/text()[normalize-space()]').extract_first().replace('B M W', 'BMW').replace('Ssang Yong', 'SsangYong')
        if title:
            item['title'] = title
            year = re.search(r'[1-3][0-9]{3}', title)
            if year:
                item['year'] = year.group()
            # make = [word for word in make_list.values() if word in title]
            for key, value in make_list.items():
                if re.search(r'\b' + value + r'\b', title):
                    item['make'] = make_list[key]
                    item['key'] = key

        miles = response.xpath('//div[contains(text(), "Mileage")]/following-sibling::div/text()').extract_first()
        if miles:
            item['mileage'] = miles.replace('Miles', '').strip()

        body = response.xpath('//div[contains(text(), "Body Style")]/following-sibling::div/text()').extract_first()
        if body:
            item['body'] = body.strip()

        color = response.xpath('//div[contains(text(), "Colour")]/following-sibling::div/text()').extract_first()
        if color:
            item['exterior_color'] = color.strip()

        door = response.xpath('//div[contains(text(), "Doors")]/following-sibling::div/text()').extract_first()
        if door:
            item['door'] = door.strip()

        trans = response.xpath('//div[contains(text(), "Transmission")]/following-sibling::div/text()').extract_first()
        if trans:
            item['transmission'] = trans.strip()

        engine = response.xpath('//div[contains(text(), "Engine Size")]/following-sibling::div/text()').extract_first()
        if engine:
            item['engine_size'] = int(engine.replace('L', '').replace('.', '').strip())*100

        fuel = response.xpath('//div[contains(text(), "Fuel Type")]/following-sibling::div/text()').extract_first()
        if fuel:
            item['fuel_type'] = fuel.strip()

        co = response.xpath('//div[contains(text(), "CO2 Emission")]/following-sibling::div/text()').extract_first()
        if co:
            item['co_emission'] = co.replace('g/km', '').strip()

        tax = response.xpath('//div[contains(text(), "Tax Cost")]/following-sibling::div/a/text()').extract_first()
        if tax:
            item['tax_cost'] = tax.replace('£', '').replace('p.a.', '').strip()

        features = response.xpath('//div[contains(p/text(), "Features")]/following-sibling::div/text()').extract_first()
        if features:
            item['features'] = list(map(str.strip, re.sub(' +', ' ', features).strip().split(',')))

        description = response.xpath('//div[contains(p/text(), "Description")]/following-sibling::div/node()').extract()
        if description:
            item['description'] = re.sub(' +', ' ', ' '.join(list(map(str.strip, description))))

        image_blocks = response.xpath('//div[@id="car-images"]//div[contains(@class, "item")]')
        if image_blocks:
            images = image_blocks.xpath('./a/@href').extract()
            if images:
                # images.pop() # delete last image(possible AD)
                item['images'] = images
            else:
                images = image_blocks.xpath('.//img/@src').extract()
                if images:
                    images = [image.replace('/999999/1x', '') for image in images]
                    item['images'] = images

        price = response.xpath('//div[contains(div/text(), "Price")]/following-sibling::div//span[contains(@class, "y-big-price")]/text()').extract_first()
        if price:
            item['price'] = price.replace("£", "").strip()

        if 'key' in item:
            yield scrapy.FormRequest(
                url='https://www.usedcarsni.com/ajax_request.php?request=indexed_models:json',
                callback=self.parse_models,
                formdata={'make': item['key'], 'age_to': item['id']},
                meta={'item': item})
        else:
            yield item

    @staticmethod
    def parse_models(response):
        item = response.meta['item']
        for val in json.loads(response.body_as_unicode()):
            if re.search(r'\b' + val['name'] + r'\b', item['title']):
                item['model'] = val['name']

        return item
