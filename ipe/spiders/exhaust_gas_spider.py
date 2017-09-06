# coding:utf-8

from urllib.parse import unquote
from re import sub
import json
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector


class WaterSpider(scrapy.Spider):
    name = 'exhaust_gas'
    allowed_domains = ['ipe.org.cn']
    start_urls = ['http://www.ipe.org.cn/MapWater/water.aspx?q=2']
    headers = {
        # 'Cookie': 'ajaxkey=%s' % value,
        'Host': 'www.ipe.org.cn',
        'Origin': 'http://www.ipe.org.cn',
        'Referer': 'http://www.ipe.org.cn/MapWater/water.aspx?q=2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def start_requests(self):
        yield Request(url=self.start_urls[0], headers=self.headers, callback=self.parse,
                      meta={'pageindex': '1', 'value': None}, dont_filter=True)

    def parse(self, response):
        pageindex = response.meta['pageindex']
        value = response.meta['value']
        if value is None:
            Cookie = response.headers.getlist('Set-Cookie')
            print ('7777777777777777777777777777777',Cookie)
            value = bytes.decode(Cookie[0]).split('=')[1].split(';')[0]
            self.headers['Cookie'] = 'ajaxkey=%s' % value
        formdata = {
            'headers[Cookie]': 'ajaxkey =%s' % value,
            'cmd': 'getwater_fenye',
            'pageindex': pageindex,  # 每一次页面都需要更改 默认是第一页
            'pagesize': '8',
            'valley': '0',
            'province': '0',
            'city': 'City / Locality',
            'key': '',
            'pollution': '7',
            'enterprisids': '',
            'standardids': '0, 1, 2, 3'
        }
        yield FormRequest(url='http://www.ipe.org.cn/data_ashx/GetAirData.ashx', meta={'pageindex': pageindex, 'value':value},
                          headers=self.headers, formdata=formdata,
                          callback=self.parse_imp, dont_filter=True)

    def parse_imp(self, response):
        pageindex = response.meta['pageindex']
        value = response.meta['value']
        quHtml = response.text
        if quHtml:
            jsHtml = json.loads(quHtml)['Content']
            # js混淆解密
            html = unquote(jsHtml)
            detail = {}
            htmlx = Selector(text=html).xpath('//tbody/tr')
            for x in range(len(htmlx)):
                detail['河流'] = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                         sub('\s+', '', htmlx[x].xpath('td[1]/text()').extract_first())))
                detail['地区'] = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                         sub('\s+', '', htmlx[x].xpath('td[2]/text()').extract_first())))
                detail['断面'] = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                         sub('\s+', '', str(htmlx[x].xpath('td[3]/a/text()').extract_first()))))
                detail['水质类型'] = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                         sub('\s+', '', htmlx[x].xpath('td[4]/text()').extract_first())))

                data = {
                    'headers[Cookie]': 'ajaxkey =%s' % value,
                    'cmd': 'gethch_content',
                    'mid': htmlx[x].xpath('td[3]/a/@href').extract_first().split('(')[-1][:-2]
                }
                yield FormRequest(url='http://www.ipe.org.cn/data_ashx/GetAirData.ashx', headers=self.headers,
                                  formdata=data, meta={'item': detail},
                                  callback=self.parse_detail, dont_filter=True)
            if int(pageindex) + 1 < 1811:
                yield Request(url='http://www.ipe.org.cn/data_ashx/GetAirData.ashx', headers=self.headers,
                              callback=self.parse, meta={'pageindex': str(int(pageindex)+1), 'value': value},
                              dont_filter=True)

    def parse_detail(self, response):
        items = response.meta['item']
        quHtml = response.text
        if quHtml:
            jsHtml = json.loads(quHtml)['Content']
            # js混淆解密
            html = unquote(jsHtml)
            htmlx = Selector(text=html).xpath('//tbody/tr')
            item ={}
            for x in range(len(htmlx)):
                try:
                    key = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                            sub('\s+', '', htmlx[x].xpath('th/text()').extract_first())))
                    value = eval("u'%s'" % sub('%(u[0-9a-zA-Z]{4})', r'\\' + "\g<1>",
                                                sub('\s+', '', htmlx[x].xpath('td/text()').extract_first())))
                    item[key] = value
                except Exception:
                    pass
            items.update(item)
        yield items
