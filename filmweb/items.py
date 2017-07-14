# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field

class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    filmweb_id = Field()
    url = Field()
    title_pl = Field()
    title_or = Field()
    year = Field()
    duration = Field()
    release_date = Field()
    release_date_pl = Field()
    genre = Field()
    wants_to_see = Field()
    votes_count = Field()
    rating = Field()
    countries = Field()
    poster_url = Field()


class SerialItem(scrapy.Item):
    filmweb_id = Field()
    url = Field()
    title_pl = Field()
    title_or = Field()
    year = Field()
    genre = Field()
    votes_count = Field()
    wants_to_see = Field()
    rating = Field()
    poster_url = Field()
    episodes_data = Field()
