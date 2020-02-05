import logging
import collections

import requests
import bs4
import csv


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wb')


ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS={
    'Бренд',
    'Товар',
    'Ссылка',
}

class Client:
    def __init__(self):
        self.session =  requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept-Language': 'en-US,en;q=0.5',
            }
        self.result = []

    def load_page(self, page: int = None):

        url = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/rubashki'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        #logger.info(block)
        #logger.info('=' * 100)

        url_block = block.select_one('a.ref_goods_n_p')
        if not url_block:
            logger.error('no_url_block')
            return

        url = url_block.get('href')
        if not url:
            logger.error('no href')
            return

        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not name_block:
            logger.error('no name_block on {}'.format('url'))
            return

        brand_name = name_block.select_one('strong.brand-name')
        if not brand_name:
            logger.error('no brand_name on {}'.format('url'))
            return

        #wrangler
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        goods_name = name_block.select_one('span.goods-name')
        if not goods_name:
            logger.error('no goods_name on {}'.format('url'))
            return

        goods_name = goods_name.text.strip()

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))


        logger.debug('%s, %s, %s', url, brand_name, goods_name)
        logger.debug('-' * 100)


    def save_result(self):
        path = '/home/rafayel/Desktop/My_projects/Parsing/wildberries/wild_parse/rubashki_result.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)


    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info('Получили {} элементов'.format(len(self.result)))

        self.save_result()



if __name__ == '__main__':
    parser = Client()
    parser.run()
