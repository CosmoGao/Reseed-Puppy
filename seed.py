from config.site_config import sites
from log import writeLog
import bencodepy
import requests
import hashlib
import json
import os
logger = writeLog('my_logger', 'log/reseed.log')
def seed():
  folder_path = 'torrents'
  pieces_hash = []
  fz_array = []
  logger.info('辅种脚本启动')
  for file_name in os.listdir(folder_path):
    if file_name.endswith('.torrent'):
      file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'rb') as f:
      torrent_data = f.read()
      torrent = bencodepy.decode(torrent_data)
      info = torrent[b'info']
      pieces = info[b'pieces']
      piece_length = info[b'piece length']
      sha1 = hashlib.sha1(pieces).hexdigest()
      pieces_hash.append(sha1)
  logger.info("当前种子库：" + str(len(pieces_hash)) + "个种子")
  for site in sites:
    if(site['passkey'] != ''):
      headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
      }
      data = {
        "passkey": site['passkey'],
        "pieces_hash": pieces_hash
      }
      url = site['apiUrl']
      try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
      except requests.exceptions.Timeout:
        logger.info('站点请求时间超过5秒：'+site['apiUrl'])
        continue
      if response.status_code == 200:
        response_json = json.loads(response.text)
        values =  response_json['data'].values()
        for value in values:
          logger.info(site['siteName']+"可辅种id值："+str(value))
          fz_array.append(site['siteUrl'] +'download.php?id='+str(value)+'&passkey='+site['passkey'])
    else:
      logger.info(site['siteName']+"没有填写passkey")
  logger.info("可辅种数："+str(len(fz_array))+"个种子")
  logger.info(fz_array)
  logger.info("辅种结束")