import multiprocessing
import os

import requests

import common.env as env


def check_proxy(proxy):
    result = None

    try:
        r = requests.get('https://www.google.com', proxies={'https': 'https://' + proxy}, timeout=3)

        if r.status_code == 200:
            message = 'OK'
            result = proxy
        else:
            message = 'status code ' + str(r.status_code)
    except requests.exceptions.ProxyError:
        message = 'proxy error'
    except requests.exceptions.ConnectTimeout:
        message = 'connection timeout'
    except requests.RequestException as e:
        message = repr(e)

    print(proxy + ' - ' + message)

    return result


proxies_file_name = env.DATA_DIR + '/proxies.lst'

proxies = []

if os.path.isfile(proxies_file_name):
    with open(proxies_file_name, 'r') as f:
        proxies = f.read().splitlines()

f = requests.get('https://www.proxy-list.download/api/v1/get?type=https')
proxies = proxies + f.text.splitlines()
proxies = filter(None, proxies)
proxies = list(set(proxies))

with multiprocessing.Pool(processes=30) as pool:
    good_proxies = list(filter(None, pool.map(check_proxy, proxies)))

with open(proxies_file_name, 'w') as f:
    for proxy in good_proxies:
        print(proxy, file=f)
