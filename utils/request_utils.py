import requests
import os
import os.path as osp
import random
import sys

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
    'Opera/8.0 (Windows NT 5.1; U; en)',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 ',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'
]

def getHeaders():
    i = random.randint(0, 10)
    user_agent = user_agents[i]
    headers = {
        'User-Agent': user_agent
    }
    return headers


def get_page(url, justText=True):
    headers=getHeaders()
    response = requests.get(url,headers=headers)
    if justText:
        return response.text
    else:
        return response


def save_page(html, save_file_path):
    # 将 html 文本形式保存
    with open(save_file_path,'w') as f:
        f.write(html)


def get_page_v2(url, save_file_path="", justText=True):
    if osp.exists(save_file_path) and justText:
        return dict(text=open(save_file_path,'r').read(),status_ok=True, response=None)
    else:
        response = get_page(url,False)
        if response.status_code!=200:
            print("Page not requested, response.status_code:",response.status_code)
            return dict(text=response.text, status_ok=False, response=response)
        if save_file_path!="":
            try:
                filename = save_file_path.split('/')[-1]
                save_dir = save_file_path[:-len(filename)]
                if not osp.exists(save_dir):
                    os.system(f"mkdir -p {save_dir}")
                save_page(response.text, save_file_path)
                print(f'save page ok: {save_file_path}')
            except:
                print(f'save page error: {save_file_path}')
        return dict(text=response.text,status_ok=True,response=response)
