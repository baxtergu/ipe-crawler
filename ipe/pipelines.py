# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class MongodbPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='10.45.4.204', port=27017)
        self.db = self.client['ipe']
        self.coll = self.db['test01']

    def process_item(self, item, spider):
        postItem = dict(item)
        self.coll.insert(postItem)
        return item