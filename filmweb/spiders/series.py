import scrapy
from ..items import SerialItem
import hashlib
import json

class SeriesScraper(scrapy.Spider):
    name = 'series'

    def start_requests(self):
        url = 'http://www.filmweb.pl/rankings/serial/country?country=&genre=&year='
        years = ['2016', '2017']
        for year in years:
            url2 = url + year
            yield scrapy.Request(url=url2, callback=self.parse)

    def parse(self, response):
        seriale = response.css('.rankingTable tr[id^=p] td[class~=element] a::attr(href)').extract()
        for serial in seriale:
            url2 = 'http://filmweb.pl' + serial + '/episodes'
            yield scrapy.Request(url=url2, callback=self.parse_serial)

    def parse_serial(self, response):
        item = SerialItem()
        item['filmweb_id'] = response.css('.filmMainHeader').re('(?<=setFilmWithParams\().*?(?=,\{)')[0]
        item['url'] = response.url
        item['episodes_data'] = []
        episodesdata = response.css('.episodesTable dd[class=expanded]')
        for sezon, episode in enumerate(episodesdata):
            odcinki = episode.css('ul li')
            for nr, odcinek in enumerate(odcinki):
                premiera = odcinek.css('div[class^=dates] div::attr(data-date-premiere)')[0].extract()
                item['episodes_data'].append({'sezon': sezon + 1, 'odcinek': nr + 1, 'premiera': premiera })
        apiurl = filmwebapi_md5(item['filmweb_id'])
        content = response.css('.filmPosterBox div#filmPosterLink::text').extract()
        if content:
            content = content[0].replace('.5.jpg', '.3.jpg')
            item['poster_url'] = content
        yield scrapy.Request(url=apiurl, callback=self.parse_api, meta={'item': item})

    def parse_api(self, response):
        item = response.meta.get('item')
        text = str(response.text).replace('ok\n', '').replace(' t:43200\n', '')
        text = json.loads(text)
        item['title_pl'] = text[0]
        item['title_or'] = text[1]
        item['genre'] = text[4]
        item['rating'] = text[2]
        item['votes_count'] = text[3]
        item['year'] = text[5]

        return item

def filmwebapi_md5(filmwebid):
    stringtohash = 'getFilmInfoFull [' + str(filmwebid) + ']\nandroidqjcGhW2JnvGT9dfCt3uT_jozR3s'
    md5hash = hashlib.md5(stringtohash.encode('utf-8')).hexdigest()
    url = 'https://ssl.filmweb.pl/api?version=1.0&appId=android&methods=getFilmInfoFull%20[' + str(filmwebid) + ']\n&signature=1.0,' + md5hash
    return url