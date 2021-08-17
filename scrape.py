#!/usr/bin/python3
# Modified from https://www.scrapehero.com/scrape-yahoo-finance-stock-market-data/
# Zach Pomper, 2019

from lxml import html
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
import re
import pandas as pd
import urllib3
import aiohttp
import asyncio

def url_gen(ticker):
  return "https://finance.yahoo.com/quote/%s/analysis?p=%s"%(ticker,ticker)

def parse(retd):
  ticker, response = retd['ticker'], retd['response']
  url = url_gen(ticker)
  parser = html.fromstring(response)
  # The number 42 here is actually a regex that matches the correct table,
  # which has an ID between 420 and 430. I was at first concerned that
  # this had changed over time, but it doesn't seem to have done, thankfully.
  summary_table = parser.xpath('//tr[contains(@data-reactid,"42")]')
  summary_data = OrderedDict()
  # print(summary_table)
  # print(summary_data)
  try:
    for table_data in summary_table:
      raw_table_key = table_data.xpath('.//td[contains(@class,"Ta(start)")]//text()')
      raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
      table_key = ''.join(raw_table_key).strip()
      table_value = ''.join(raw_table_value).strip()
      if ("N/A" in table_value):
        new_val = re.sub("N|A|/", "",table_value)
        summary_data.update({table_key:new_val})
        # print(new_val, ticker)
      else:
        summary_data.update({table_key:table_value})
    summary_data.update({'ticker':ticker,'url':url})
    return summary_data
  except:
    print ("Failed to parse json response")
    return {"error":"Failed to parse json response"}

async def fetch(url, ticker, session):
    async with session.get(url, headers={'Connection': 'keep-alive'}) as response:
        response = await response.text()
        return {'response': response, 'ticker': ticker}

from aiohttp.client_reqrep import ClientRequest
import socket
class KeepAliveClientRequest(ClientRequest):
  async def send(self, conn: "Connection") -> "ClientResponse":
    sock = conn.protocol.transport.get_extra_info("socket")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
    return (await super().send(conn))

async def run(urls):
  tasks = []
  async with aiohttp.ClientSession(request_class=KeepAliveClientRequest) as session:
    for d in urls:
      url = d['url']
      ticker = d['ticker']
      task = asyncio.ensure_future(fetch(url, ticker, session))
      tasks.append(task)
    retds = await asyncio.gather(*tasks)
    return retds

def async_agg():
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  gh_csv = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
  data = pd.read_csv(gh_csv)
  aggregate_data = {}
  urls = []
  for index, row in data.iterrows():
    if index != 0:
      ticker = row['Symbol']
      url = url_gen(ticker)
      urls.append({'url': url, 'ticker': ticker})

  loop = asyncio.get_event_loop()
  future = asyncio.ensure_future(run(urls))
  retds = loop.run_until_complete(future)

  for retd in retds:
    scraped_data = parse(retd)
    # print (scraped_data)
    try:
      d = {scraped_data['ticker']: scraped_data['Next 5 Years (per annum)']}
      aggregate_data.update(d)
    except:
      pass
  return aggregate_data

if __name__=="__main__":
  aggregate_data = async_agg()
  with open('aggregate_data.json','w') as fp:
    json.dump(aggregate_data,fp,indent = 4)