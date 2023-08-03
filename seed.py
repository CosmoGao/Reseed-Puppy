import os
import hashlib
import json
import requests
from log import writeLog
import bencodepy
from config.site_config import sites
import qbittorrentapi

logger = writeLog('my_logger', 'log/reseed.log')
# instantiate a Client using the appropriate WebUI configuration
conn_info = dict(
    host="",
    port=8080,
    username="admin",
    password="adminadmin",
)
qbt_client = qbittorrentapi.Client(**conn_info)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# if the Client will not be long-lived or many Clients may be created
# in a relatively short amount of time, be sure to log out:
# qbt_client.auth_log_out()

def seed():
    folder_path = 'torrents'
    pieces_hash_list = []
    fz_array = []
    info_hash_topieces = {}
    logger.info('辅种脚本启动')
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.torrent'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'rb') as f:
                torrent_data = f.read()
                torrent = bencodepy.decode(torrent_data)
                info = torrent[b'info']
                pieces = info[b'pieces']
                info_sha1 = hashlib.sha1(bencodepy.encode(info)).hexdigest()
                pieces_sha1 = hashlib.sha1(pieces).hexdigest()
                pieces_hash_list.append(pieces_sha1)
                info_hash_topieces[pieces_sha1] = info_sha1

    logger.info("当前种子库：%d 个种子", len(pieces_hash_list))
    for site in filter(lambda x: x['passkey'], sites):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "passkey": site['passkey'],
            "pieces_hash": pieces_hash_list
        }
        url = site['apiUrl']
        try:
            response = requests.post(url, headers=headers, json=data, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning('站点请求失败：%s - %s', site['siteName'], e)
            continue

        response_json = response.json()
        if isinstance(response_json.get('data'), dict):
            for value in response_json['data']:
                torrent_info = qbt_client.torrents_info(torrent_hashes=info_hash_topieces[value])
                if(torrent_info):
                    save_path = torrent_info[0]['save_path']
                    if qbt_client.torrents_add(urls=f"{site['siteUrl']}download.php?id={response_json['data'][value]}&passkey={site['passkey']}",save_path=save_path) == "Ok.":
                        logger.info("种子pieces_info%s",value)
                        logger.info("%s 可辅种 id：%d正在添加到下载器中", site['siteName'],  response_json['data'][value])
                    fz_array.append(f"{site['siteUrl']}download.php?id={response_json['data'][value]}&passkey={site['passkey']}")
        else:
            logger.info("%s 没有可辅种的种子", site['siteName'])

    logger.info("可辅种数：%d 个种子", len(fz_array))
    logger.info(fz_array)
    logger.info("辅种结束")