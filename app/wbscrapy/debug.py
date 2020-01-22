from scrapy import cmdline


#cmdline.execute("scrapy crawl products -o debug.json -t json -a type=new".split())
cmdline.execute("scrapy crawl products -o debug.json -t json".split())
