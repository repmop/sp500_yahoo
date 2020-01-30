# Modified from https://www.scrapehero.com/scrape-yahoo-finance-stock-market-data/
# Zach Pomper, 2019

from lxml import html
import traceback
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import re
import pandas as pd
import urllib3


def parse(ticker):
  url = "http://finance.yahoo.com/quote/%s/analysis?p=%s"%(ticker,ticker)
  response = requests.get(url, verify=False)
  sleep(4)
  parser = html.fromstring(response.text)
  summary_table = parser.xpath('//tr[contains(@data-reactid,"43")]')
  summary_data = OrderedDict()
  other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(ticker)
  summary_json_response = requests.get(other_details_json_link)
  try:
    json_loaded_summary =  json.loads(summary_json_response.text)
    earnings_list = json_loaded_summary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
    for table_data in summary_table:
      raw_table_key = table_data.xpath('.//td[contains(@class,"Ta(start)")]//text()')
      raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
      table_key = ''.join(raw_table_key).strip()
      table_value = ''.join(raw_table_value).strip()
      if ("N/A" in table_value):
        new_val = re.sub("N|A|/", "",table_value)
        summary_data.update({table_key:new_val})
        print(new_val)
      else:
        summary_data.update({table_key:table_value})
    summary_data.update({'ticker':ticker,'url':url})
    return summary_data
  except Exception as e:
    traceback.print_exc()
    return {"eror":"Failed to parse json response"}

def runticker(ticker):
  print ("Fetching data for %s"%(ticker))
  scraped_data = parse(ticker)
  print ("Writing data to output file")
  with open('%s-summary.json'%(ticker),'w') as fp:
    json.dump(scraped_data,fp,indent = 4)
  d = None
  try:
    d = {scraped_data['ticker']: scraped_data['Past 5 Years (per annum)']}
  except:
    pass
  return d


if __name__=="__main__":
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
  table = data[0]
  aggregate_data = {}
  try:
    for index, row in table.iterrows():
      if index != 0:
        symbol = row['Symbol']
        symbol = re.sub("\.", "-", symbol)
        d = runticker(symbol)
        if d != None:
          aggregate_data.update(d)
    print(aggregate_data)
    with open('aggregate_data.json','w') as fp:
      json.dump(aggregate_data,fp, sort_keys = True, indent = 4)
  except KeyboardInterrupt:
    print(aggregate_data)
    with open('aggregate_data.json','w') as fp:
      json.dump(aggregate_data,fp, sort_keys = True, indent = 4)
