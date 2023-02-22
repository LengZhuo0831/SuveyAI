from selenium import webdriver
from tqdm import tqdm
import os
import json
from bs4 import BeautifulSoup

def get_options():
    options = webdriver.ChromeOptions()
    # 设置参数
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option('useAutomationExtension', False)
    # 带入参数和插件地址 并执行Chrome
    driver = webdriver.Chrome(options=options)
    # 方法可以用来执行Chrome开发这个工具命令。
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        # 这里的操作大概就是把控制台中的window.navigator.webdriver =undefined  赋值   因为人机操作会认为是Ture
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    return driver

class GoogleUtil:
    def __init__(self) -> None:
        self.browser = get_options()
        self.browser.get('https://www.baidu.com')
        pass
    def parse_paper(self, url=None, paper_name=''):
        if url==None:
            assert paper_name!=''
            url = f'https://scholar.google.com/scholar?hl=en&q={paper_name}'
        self.browser.get(url)
        a = input("print ENTER to continue...")
        html = BeautifulSoup(self.browser.page_source, 'html.parser')
        ori_paper_name = paper_name
        res_all = []
        cards = html.find_all("div", attrs={"class": "gs_r gs_or gs_scl"})
        assert len(cards)>0, 'block'
        for card in cards:
            if len(card.contents)==2:
                paper_url = card.div.div.div.a['href']
                contents = card.contents[1]
            else:
                paper_url = ''
            paper_name = contents.h3.a.text
            author_source_info = contents.contents[1].text

            # author citation
            author_page_urls = []
            for element in contents.contents[1].contents:
                try:
                    author_page_url = element['href']
                    author_name = element.text
                except:
                    author_page_url = ''
                    author_name = element.text
                author_page_urls.append((author_name, author_page_url))
                if author_page_url!='':
                    pass
                    # author_info = parseAuthorPage(author_page_url)

            # citation
            citation = contents.contents[3].text

            rrr = dict(paper_url=paper_url,paper_name=paper_name,author_source_info=author_source_info,author_page_urls=author_page_urls,citation=citation)
            res_all.append(rrr)
        
        return res_all






