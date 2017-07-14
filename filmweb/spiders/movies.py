import scrapy
from ..items import MovieItem
import regex
import hashlib
import json

class MoviesSpider(scrapy.Spider):
    name = 'movies'

    def start_requests(self):
        """ how many pages to scrap, and starting link"""
        url = 'http://www.filmweb.pl/search/film?q=&startYear=1888&endYear=&startRate=&endRate=&startCount=&endCount=&sort=COUNT&sortAscending=false&page='
        for i in range(1, 5):
            url2 = url + str(i)
            yield scrapy.Request(url=url2, callback=self.parse)

    def parse(self, response):
        """ lets get all movies on current page """
        page = response.url.split('page=')[1]
        page_movies = response.css('.entityTitle a::attr(href)').extract()
        for movie in page_movies:
            movieurl = 'http://filmweb.pl' + movie
            yield scrapy.Request(url=movieurl, callback=self.parse_movie)


    def parse_movie(self, response):
        """ lets parse url and filmwebid for movie and then pass it to api parser"""
        item = MovieItem()
        item['filmweb_id'] = response.css('.filmMainHeader').re('(?<=setFilmWithParams\().*?(?=,\{)')[0]
        item['url'] = response.url
        # sprawdzmy plakat
        content = response.css('.filmPosterBox div#filmPosterLink::text').extract()
        if content:
            content = content[0].replace('.5.jpg', '.3.jpg')
            item['poster_url'] = content
        # sprawdzmy ilosc glosow
        content =  response.css('.communityRateInfoWrapper').extract()
        if content:
            a = regex.search('(?<=(głosy|głos|głosów)</div></div>).*?(?=\ chce)', content[0])
            if a:
                item['wants_to_see'] = a[0].replace(' ', '')
            else:
                item['wants_to_see'] = '0'
        # stworzy url dla api i parsujmy je
        apiurl = filmwebapi_md5(item['filmweb_id'])
        yield scrapy.Request(url=apiurl, callback=self.parse_api, meta={'item': item})

    def parse_api(self, response):
        item = response.meta.get('item')
        text = str(response.text).replace('ok\n', '').replace(' t:43200\n', '')
        text = json.loads(text)
        item['release_date'] = text[13]
        item['release_date_pl'] = text[14]
        item['countries'] = text[18]
        item['genre'] = text[4]
        item['rating'] = text[2]
        item['votes_count'] = text[3]
        item['duration'] = text[6]
        item['year'] = text[5]
        item['title_pl'] = text[0]
        item['title_or'] = text[1]
        return item


""" function to create link for filmweb api """
def filmwebapi_md5(filmwebid):
    stringtohash = 'getFilmInfoFull [' + str(filmwebid) + ']\nandroidqjcGhW2JnvGT9dfCt3uT_jozR3s'
    md5hash = hashlib.md5(stringtohash.encode('utf-8')).hexdigest()
    url = 'https://ssl.filmweb.pl/api?version=1.0&appId=android&methods=getFilmInfoFull%20[' + str(filmwebid) + ']\n&signature=1.0,' + md5hash
    return url

        # other method
        # item['year'] = response.css('.halfSize::text').extract()[0].replace('(', '').replace(')', '').replace(' ', '')