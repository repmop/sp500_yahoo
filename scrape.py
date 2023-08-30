#!/usr/bin/python3
# Modified from https://www.scrapehero.com/scrape-yahoo-finance-stock-market-data/
# Zach Pomper, 2021

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


class TickerInfo:
    def __init__(self, ticker, url):
        self.ticker = ticker
        self.url = url
        self.table = {}

def url_gen(ticker):
  return "https://finance.yahoo.com/quote/%s/analysis?p=%s"%(ticker,ticker)

def parse(retd):
  ticker, response = retd['ticker'], retd['response']
  parser = html.fromstring(response)
  response = parser.text_content()
  url = url_gen(ticker)
  exp = r'(?:Next 5 Years \(per annum\))([0-9\.-]+%)'
  matches = re.findall(exp, response)

  ret = TickerInfo(ticker, url)
  if len(matches) > 0:
    ret.table.update({'Next 5 Years (per annum)':matches[0]})
  else:
    ret.table.update({'Next 5 Years (per annum)':""})
  return ret




async def fetch(url, ticker, session):
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
      'Connection': 'keep-alive'
    }
    async with session.get(url, headers=headers) as response:
        response = await response.text()
        return {'response': response, 'ticker': ticker}

from aiohttp.client_reqrep import ClientRequest
import socket
class KeepAliveClientRequest(ClientRequest):
  async def send(self, conn: "Connection") -> "ClientResponse":
    sock = conn.protocol.transport.get_extra_info("socket")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
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
    try:
      d = {scraped_data.ticker: scraped_data.table['Next 5 Years (per annum)']}
      aggregate_data.update(d)
    except:
      pass
  return aggregate_data

if __name__=="__main__":
  aggregate_data = async_agg()
  with open('aggregate_data.json','w') as fp:
    json.dump(aggregate_data,fp,indent = 4, sort_keys=True)
