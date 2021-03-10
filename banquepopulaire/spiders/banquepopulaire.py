import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from banquepopulaire.items import Article


class BanquepopulaireSpider(scrapy.Spider):
    name = 'banquepopulaire'
    start_urls = ['https://www.banquepopulaire.fr/portailinternet/Editorial/Informations/Pages/actualites.aspx']

    def parse(self, response):
        links = response.xpath('//a[@title="En savoir plus"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="block"]//text()').getall()
        content = [text for text in content if text.strip()]

        date = response.xpath('//h2[@class="ibp-rteElement-H2"]/text()').get()
        if date and (date.split('/')[-1].strip().isnumeric() or date.lower().startswith('le ')):
            date = " ".join(date.strip().split()[1:])
            content.pop(0)
        else:
            date = ''

        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
