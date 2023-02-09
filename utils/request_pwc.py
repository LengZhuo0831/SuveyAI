
import requests
import re
import json
from bs4 import BeautifulSoup
import pandas as pd
import random
from tqdm import tqdm
import os
try:
    from request_utils import get_page, get_page_v2, save_page
except:
    from .request_utils import get_page, get_page_v2, save_page


class PwcTools:
    def parse(html, mode, **kwargs):
        # mode: query, paper, benchmark, dataset, task 五种类型
        assert mode in ['query', 'paper', 'benchmark', 'dataset', 'task', 'method']
        return eval(f'PwcTools.parce_{mode}(html, **kwargs)')


    def parce_query(html, **kwargs):
        print("parsing query...")
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']
        cards = soup.find_all("div",attrs={"class":"row infinite-item item paper-card"})
        results = []
        for card in cards:
            content = card.find("div",attrs={"class":"col-lg-9 item-content"})
            paper_name = content.h1.a.text
            paper_url = content.h1.a['href']
            code_info = content.p.a.text
            date_info = content.p.find("span",attrs={"class":"author-name-text item-date-pub"})
            date_info = date_info.text.strip() if date_info!=None else ""
            conference_info = content.p.find("span",attrs={"class":"item-conference-link"})
            conference_info = conference_info.text.strip() if conference_info!=None else ""
            other_info = content.p.find("span")
            other_info = other_info.text.strip() if other_info!=None else ""

            strip_abstract = content.find("p",attrs={"class":"item-strip-abstract"}).text

            tasks = content.find_all("span",attrs={"class":"badge badge-primary"})
            tasks = [task.text.strip() for task in tasks]

            content2 = card.find("div",attrs={"class":"col-lg-3 item-interact text-center"})
            star = content2.find("div",attrs={"class":"entity-stars"}).text
            paper_url2 = content2.find("div",attrs={"class":"entity"}).a['href']

            results.append(
                dict(
                    paper_name=paper_name,
                    paper_url=paper_url,
                    code_info = code_info,
                    date_info = date_info,
                    conference_info = conference_info,
                    other_info = other_info,
                    strip_abstract = strip_abstract,
                    tasks = tasks,
                    star = star,
                    paper_url2 = paper_url2
                )
            )
        
        return dict(page_title=page_title,page_url=page_url,results=results)


    def parce_paper(html, **kwargs):
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']

        infos1 = soup.find("div", attrs={"class":"paper-title"})
        paper_title = infos1.div.div.h1.text.strip()
        author_infos = infos1.find("div", attrs={"class":"authors"})
        conference_info = author_infos.find("span",attrs={"class":"item-conference-link"})
        conference_info = conference_info.a.text.strip() if conference_info!=None else ""
        date = ""
        authors = author_infos.find_all("span", attrs={"class":"author-span"})
        authors = [author.text.strip() for author in authors]
        if len(authors)>0:
            if re.match(r'[1-9]* ([a-z]|[A-Z])* [1-9]*',authors[0]):
                # 说明第一个元素是时间
                date = authors[0]
                authors = authors[1:]
            else:
                date = conference_info

        # abstract
        infos2 = soup.find("div", attrs={"class":"paper-abstract"})
        if infos2:
            abstract = infos2.div.div.p.text.strip()
            paper_urls = []
            a_panels = infos2.div.div.find_all('a')
            for a in a_panels:
                if "PDF" in a.text:
                    paper_urls.append(a['href'])
                else:
                    continue
        else:
            abstract = ""
            paper_urls = []
        
        # code
        info3 = soup.find("div", attrs={"id":"code"})
        codes = info3.find("div", attrs={"id":"implementations-full-list"})
        code_lst = []
        for raw in codes.find_all("div", attrs={"class":"row"}):
            raw1 = raw.find("div",attrs={"class":"col-sm-7"})
            link = raw1.find("div",attrs={"class":"paper-impl-cell"}).a['href']

            raw2 = raw.find("div",attrs={"class":"col-3"})
            star = raw2.div.text.strip()

            raw3 = raw.find("div",attrs={"class":"col-2"})
            platform_link = raw3.div.img['src'] if raw3.div.img!=None else 'unknown'

            code_lst.append((link, star, platform_link))


        info4 = soup.find("div", attrs={"id":"tasks"})
        tasks = info4.find("div", attrs={"class":"paper-tasks"})
        tasks = tasks.div.div.find_all('a')
        task_lst = []
        for task in tasks:
            task_lst.append((task['href'], task.span.span.text.strip()))
        
        # datasets
        info5 = soup.find("div", attrs={"id":"datasets"})
        datasets = info5.find("div", attrs={"class":"paper-datasets"})
        datasets = datasets.div.div.find_all('a')
        datasets_lst = []
        for dst in datasets:
            datasets_lst.append((dst['href'],dst.text.strip()))

        # sota table
        info6 = soup.find("div", attrs={"class":"sota-table table-responsive"})
        if info6!=None:
            table = info6.table
            records = table.find_all('tr')
            table_length = 0
            keys = []
            sota_records_list = []
            for ind, record in enumerate(records):
                rrr = dict()
                if ind==0:
                    items = record.find_all('th')
                else:
                    items = record.find_all('td')
                if ind==0:
                    table_length = len(items)
                    for item in items:
                        keys.append(item.text.strip())
                elif len(items)==table_length:
                    for iind, item in enumerate(items):
                        if iind < 6:
                            rrr[keys[iind]]=item.text.strip()
                        elif iind==6:
                            try:
                                rrr[keys[iind]]=item.a['href']
                            except:
                                rrr[keys[iind]]=''
                        else:
                            try:
                                rrr[keys[iind]]=item.div.a['href']
                            except:
                                rrr[keys[iind]]=''
                    sota_records_list.append(rrr)
                elif len(items)==table_length-3:
                    for iind in range(table_length):
                        if iind<3:
                            rrr[keys[iind]]=sota_records_list[-1][keys[iind]]
                        elif iind<6:
                            rrr[keys[iind]]=items[iind-3].text.strip()
                        elif iind==6:
                            # rrr[keys[iind]]=items[iind-3].a['href']
                            try:
                                rrr[keys[iind]]=items[iind-3].a['href']
                            except:
                                rrr[keys[iind]]=''
                        else:
                            # rrr[keys[iind]]=items[iind-3].div.a['href']
                            try:
                                rrr[keys[iind]]=items[iind-3].div.a['href']
                            except:
                                rrr[keys[iind]]=''
                    sota_records_list.append(rrr)
                else:
                    raise ValueError
        else:
            sota_records_list = []

        # method
        info7 = soup.find("div", attrs={"class":"method-section"})
        methods = info7.find_all('a')
        if 'No methods listed for this paper' in info7.text:
            methods_lst = []
        else:
            methods_lst = []
            for m in methods:
                methods_lst.append((m['href'],m.text.strip()))

        print("parsing paper...")

        return dict(
            page_url=page_url,
            page_title=page_title,
            paper_title=paper_title,
            paper_urls=paper_urls,
            authors=authors,
            conference_info=conference_info,
            date=date,
            abstract=abstract,
            code_lst=code_lst,
            datasets_lst=datasets_lst,
            task_lst=task_lst,
            sota_records_list=sota_records_list,
            methods_lst=methods_lst,
        )


    def parce_benchmark(html,**kwargs):
        print("parsing benchmark...")
        '''
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']
        info1 = soup.find("table", attrs={"class":"table-striped show-overflow-x"})
        if info1!=None:
            return []
        keys = info1.thead.find_all('th')
        keys = [th.text.strip() for th in keys]
        records = info1.find_all('tr')
        records_lst = []
        for record in records:
            rrr = dict()
            items = record.find_all('td')
            assert len(items)==len(keys)
            for iind, item in enumerate(items):
                if iind==1:
                    method_name = item.div.a.text.strip()
                    append_info = item.div.a.find('span',attrs={"class":"small"})
                    append_info = append_info.text.strip() if append_info!=None else ""
                    rrr[keys[iind]]=method_name+' '+append_info
                elif iind==6:
                    # extra data training
                    name = item.svg.name
                    extra_data_training = False if name=='close' else True
                    rrr[keys[iind]]=extra_data_training
                elif iind==7:
                    # paper and url
                    paper_name, paper_url = item.div.a.text.strip(), item.div.a['href']
                    rrr[keys[iind]]=(paper_name, paper_url)
                elif iind==10:
                    tags = item.find_all('span',attrs={"class":"badge sota-row-tags"})
                    tags = [tag.text.strip() for tag in tags]
                    rrr[keys[iind]] = tags
                else:
                    rrr[keys[iind]] = item.text.strip()
        
            records_lst.append(rrr)
        return records_lst
        '''
        sota_list = re.findall(r'\[{"table_id": [\S\s]*?\]<',html)
        if len(sota_list)==0:
            return []
        assert len(sota_list)==1
        text = sota_list[0][:-1]
        text = text.replace("null","None").replace("true","True").replace("false","False")
        sota_list = eval(text)
        print('records length:',len(sota_list))
        # 重要字段：rank, method, method_details, evaluation_date, metrics, uses_additional_data, paper, tags
        return sota_list


    def parce_dataset(html,**kwargs):
        print("parsing dataset...")
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']

        infos1 = soup.find("div", attrs={"class":"dataset-title mb-3"})
        title = infos1.find('h1').text.strip()
        paper = infos1.find("span", attrs={"class":"dataset-subtitle"})
        paper_url, paper_title = paper.a['href'], paper.text.strip()
            
        abstract = soup.find("div", attrs={"class":"description-content"})
        abstract, source_url = abstract.p.text.strip(), abstract.span.a['href']

        # benchmarks
        benchmarks = soup.find("table", attrs={"id":"benchmarks-table"})
        keys = benchmarks.thead.find_all('th')
        keys = [key.text.strip() for key in keys]
        records = benchmarks.tbody.find_all('tr')
        benchmark_lst = []
        for record in records:
            rrr = dict()
            items = record.find_all('td')
            for iind, item in enumerate(items):
                if iind==1:
                    rrr[keys[iind]]=(item.div.a['href'],item.div.a.text.strip())
                elif iind==2 or iind==3:
                    rrr[keys[iind]]=item.div.text.strip()
                elif iind==4:
                    rrr[keys[iind]]=item.div.a['href'] if item.div!=None else ""
                else:
                    continue
            benchmark_lst.append(rrr)

        '''
        # papers
        papers = soup.find("table", attrs={"id":"datatable-papers"})
        # https://paperswithcode.com/api/internal/papers/?paperdataset__dataset_id=4884&page=3&search=&ordering=has_repo%2C-best_papergithubrepo__githubrepo__stars
        keys = papers.thead.find_all('th')
        keys = [key.text.strip() for key in keys]
        records = papers.tbody.find_all('tr')
        paper_lst = []
        for record in records:
            rrr = dict()
            items = record.find_all('td')
            for iind, item in enumerate(items):
                
                if iind==0:
                    paper_info = item.find("div", attrs={"class":"black-links"})
                    author_info = item.find("div", attrs={"class":"grey-links"})
                    rrr[keys[iind]] = (paper_info.a['href'],paper_info.a.text.strip(),author_info.text.strip().split(','))
                elif iind==1 or iind==2:
                    continue
                elif iind==3 or iind==4:
                    rrr[keys[iind]] = item.div.text.strip() if item.div!=None else ""
            paper_lst.append(rrr)
        '''

        # papers 
        dst_id = 4884
        dst_id = re.findall(r"const DATATABLE_PAPERS_FILTER_VALUE = '[0-9]*'",html)
        assert len(dst_id)==1, dst_id
        dst_id = dst_id[0][39:-1]
        api_url = f"https://paperswithcode.com/api/internal/papers/?paperdataset__dataset_id={dst_id}&page=1&search=&ordering=has_repo%2C-best_papergithubrepo__githubrepo__stars"
        # page = get_page(api_url)
        save_root = 'cache' if 'save_root' not in kwargs else kwargs['save_root']
        page = get_page_v2(api_url, os.path.join(save_root,'dataset',f"{dst_id}_pg1.txt"))['text']
        all_papers = []
        results = eval(page.replace("null","None").replace("true","True").replace("false","False"))
        all_papers.extend(results['results'])
        count = results['count']
        MAX_PAGE = 5 if 'MAX_PAGE' not in kwargs else kwargs['MAX_PAGE']
        for i in range(min(count//10,MAX_PAGE-1)):
            # api_url = f"https://paperswithcode.com/api/internal/papers/?paperdataset__dataset_id={dst_id}&page={i+2}&search=&ordering=has_repo%2C-best_papergithubrepo__githubrepo__stars"
            api_url = results['next']
            # page = get_page(api_url)
            page = get_page_v2(api_url, os.path.join(save_root,'dataset',f"{dst_id}_pg{i+2}.txt"))['text']
            results = eval(page.replace("null","None").replace("true","True").replace("false","False"))
            all_papers.extend(results['results'])
        
        # dataloader code
        codes = soup.find("div", attrs={"class":"dataloader-container"})
        codes = codes.find("ul", attrs={"class":"dataloader-implementations"})
        codes = codes.find_all("div", attrs={"class":"row"})
        codes_lst = []
        for code in codes:
            items = [code.find("div", attrs={"class":"col-md-7"}),
            code.find("div", attrs={"class":"col-3"}),
            code.find("div", attrs={"class":"col-md-2"})]
            link = items[0].div.a['href']
            stars = items[1].div.text.strip()
            plat_imgs = [img['src'] for img in items[2].find_all('img')]
            codes_lst.append((link,stars,plat_imgs))

        # Tasks
        tasks = soup.find_all("div", attrs={"class":"col-md-9 description"})
        tasks = tasks[0].find_all("ul",attrs={"class":"list-unstyled"})
        assert len(tasks)==1
        tasks = tasks[0].find_all('li')
        task_lst = []
        for task in tasks:
            link = task.a['href']
            name = task.a.span.span.text.strip()
            task_lst.append((link, name))
        
        # similar dataset
        similar_datasets = soup.find_all("div", attrs={"class":"card-deck card-break"})
        assert len(similar_datasets)==1
        similar_datasets = similar_datasets[0].find_all("div", attrs={"class":"card"})
        similar_datasset_lst = []
        for dst in similar_datasets:
            link = dst.a['href']
            name = dst.find('h1').text.strip()
            similar_datasset_lst.append((link,name))


        return dict(
            title=title,
            page_title=page_title,
            page_url=page_url,
            paper_title=paper_title,
            paper_url=paper_url,
            abstract=abstract,
            source_url=source_url,
            benchmark_lst=benchmark_lst,
            paper_lst=all_papers,
            task_lst=task_lst,
            similar_datasset_lst=similar_datasset_lst
        )


    def parce_task(html,**kwargs):
        print("parsing task...")
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']

        task_name = soup.find("h1",attrs={"id":"task-home"}).text.strip()
        task_info = soup.find("div",attrs={"class":"artefact-information"}).p.text.strip()
        task_info = re.sub(r" (\n| )+",r"",task_info).replace('•','')
        task_info = task_info.split('\n')
        
        description = soup.find("div",attrs={"class":"description-content"})
        description = description.text.strip()
        
        # benchmarks
        benchmarks = soup.find("table", attrs={"id":"benchmarksTable"})
        if benchmarks==None:
            benchmark_lst = []
        else:
            keys = benchmarks.thead.find_all('th')
            keys = [key.text.strip() for key in keys]
            records = benchmarks.tbody.find_all('tr')
            benchmark_lst = []
            for record in records:
                rrr = dict()
                items = record.find_all('td')
                for iind, item in enumerate(items):
                    if iind==1:
                        rrr[keys[iind]]=(item.div.a['href'],item.div.a.text.strip())
                    elif iind==2 or iind==3:
                        rrr[keys[iind]]=item.div.text.strip()
                    elif iind==4:
                        rrr[keys[iind]]=item.div.a['href'] if item.div!=None else ""
                    else:
                        continue
                benchmark_lst.append(rrr)

        # libraries
        codes = soup.find("div",attrs={"id":"libraries-full-list"})
        if codes==None:
            code_lst = []
        else:
            codes = codes.find_all("div",attrs={"id":"row task-library"})
            code_lst = []
            for code in codes:
                link = code.find("div",attrs={"class":"col-12 col-md-6"}).a['href']
                paper_count = code.find("span",attrs={"class":"task-library-pwc-count"}).text.strip()
                stars = code.find("div",attrs={"class":"library-stars text-nowrap"}).text.strip()
                code_lst.append((link,paper_count,stars))

        # datasets (非全部，完整 datasets 列表需要另外的链接页面)
        datasets = soup.find("div",attrs={"class":"task-datasets"})
        if datasets==None:
            datasets_lst=[]
            datasets = ""
        else:
            datasets = datasets.find("ul",attrs={"class":"list-unstyled"})
            datasets_link = datasets.button
            datasets_link = datasets_link.parent['href'] if datasets_link!=None else ""
            datasets = datasets.find_all("li")
            datasets_lst = []
            for dst in datasets:
                datasets_lst.append(dst.text.strip())

        # sub tasks (全部)
        tasks = soup.find("div",attrs={"class":"task-subtasks"})
        if tasks==None:
            tasks_lst=[]
        else:
            tasks = tasks.find("ul",attrs={"class":"list-unstyled"})
            # tasks_link = tasks.button
            # tasks_link = tasks_link.parent['href'] if datasets_link!=None else ""
            tasks = tasks.find_all("li")
            tasks_lst = []
            for dst in tasks:
                if dst.text.strip() in tasks_lst:
                    continue
                tasks_lst.append(dst.text.strip())

        # most imp papers
        # 需要请求这个地址：{page_url}/latest?page=2
        modes = ['greatest','social','latest','codeless']
        mode = 'greatest' if 'sort_mode' not in kwargs else kwargs['sort_mode']
        assert mode in modes, mode
        MAX_PAGE=5 if 'MAX_PAGE' not in kwargs else kwargs['MAX_PAGE']
        def parse_task_paper(html):
            res = []
            cards = html.find("div",attrs={"id":"task-papers-list"})
            cards = cards.find_all("div",attrs={"class":"paper-card infinite-item"})
            for card in cards:
                card1 = card.find("div",attrs={"class":"col-lg-9 item-content"})
                card2 = card.find("div",attrs={"class":"col-lg-3 item-interact text-center"})

                res.append(dict(
                    paper_name = card1.h1.a.text.strip(),
                    paper_url = card1.h1.a['href'],
                    sub_abstract = card1.find("p",attrs={"class":"item-strip-abstract"}).text.strip(),
                    star_num = card2.div.span.text.strip()
                    )
                )
            return res

        # paper list
        paper_lst = []
        save_root = 'cache' if 'save_root' not in kwargs else kwargs['save_root']
        for i in range(MAX_PAGE):
            ppp = i+1
            if mode!='greatest':
                call_url = f"{page_url}/{mode}?page={ppp}"
            else:
                call_url = f"{page_url}?page={ppp}"
            page = get_page_v2(call_url, os.path.join(save_root,'paper',f"{task_name}_greatest_pg{ppp}.txt"))['text']
            page = BeautifulSoup(page,'html.parser')
            paper_sub_lst = parse_task_paper(page)
            paper_lst.extend(paper_sub_lst)
        
        return dict(
            task_name=task_name,
            page_title=page_title,
            page_url=page_url,
            task_info=task_info,
            description=description,
            benchmark_lst=benchmark_lst,
            datasets_lst=datasets_lst,
            datasets_link=datasets_link,
            tasks_lst=tasks_lst,
            paper_lst=paper_lst
        )


    def parce_method(html, **kwargs):
        print("parsing task...")
        soup = BeautifulSoup(html, 'html.parser')
        page_url = soup.find("meta", attrs={"property":"og:url"})['content']
        page_title = soup.find("meta", attrs={"property":"og:title"})['content']

        # method paper paper_url
        info1 = soup.find("div",attrs={"class":"method-title"})
        method_title = info1.div.div.h1.text.strip()
        method_info = info1.find("span",attrs={"class":"method-subtitle"})

        method_paper_name = None if method_info==None else method_info.a.text.strip() 
        method_paper_url = None if method_info==None else method_info.a['href']
        method_info = None if method_info==None else method_info.text.strip()

        # abstract
        content_info = soup.find("div", attrs={"class":"method-content"})
        method_content = content_info
        content_info = content_info.find("div", attrs={"class":"col-md-8 description"})
        content_info = None if content_info==None else content_info.text.strip()

        paper_num = soup.find("div",attrs={"class":"datatable-papers_info"})
        paper_num = '0' if paper_num==None else paper_num.text.strip().split(' ')[-2]

        # components
        info2 = soup.find("div",attrs={"id":"components"})
        c_table = info2.table
        items = c_table.find_all('tr')
        components = []
        if len(items)<2 or items[1].td.a==None:
            pass
        else:
            for item in items[1:]:
                components.append(
                    (
                        item.td.a['href'],
                        item.td.a.div.text.strip(),
                        item.find_all('td')[1].a['href'],
                        item.find_all('td')[1].a.text.strip()
                    )
                )

        # categories
        info3 = method_content.find("span",attrs={"class":"badge badge-primary"})
        category = info3.text.strip() if info3!=None else None


        return dict(
            method_title=method_title,
            method_info=method_info,
            method_paper_name=method_paper_name,
            method_paper_url=method_paper_url,
            components=components,
            category=category
        )



def test_query(query, tool:PwcTools):
    url = f"https://paperswithcode.com/search?q_meta=&q_type=&q={query}&page=1"
    # save_file_path = f"cache/search_{query}.html"
    save_file_path = f"cache2/query/search#{query}.html"
    res = get_page_v2(url,save_file_path)       # 
    text, status, response = res['text'], res['status_ok'], res['response']
    if not status:
        print("some thing error when getting the page, status not ok")

    return tool.parse(text, 'query')

def test_paper(url:str, tool:PwcTools):
    paper_url = 'https://paperswithcode.com' + url if url.startswith('/') else url

    save_file_path = f"cache2/paper/search#{url.replace('/','#').replace('.','*')}.html"
    res = get_page_v2(paper_url,save_file_path)       # 
    text, status, response = res['text'], res['status_ok'], res['response']
    if not status:
        print("some thing error when getting the page, status not ok")

    return tool.parse(text, 'paper')

def test_benchmark(url:str, tool:PwcTools):
    # https://paperswithcode.com/sota/open-vocabulary-object-detection-on-lvis-v1-0
    paper_url = 'https://paperswithcode.com' + url if url.startswith('/') else url
    save_file_path = f"cache2/benchmark/search#{url.replace('/','#').replace('.','*')}.html"
    res = get_page_v2(paper_url,save_file_path)       # 
    text, status, response = res['text'], res['status_ok'], res['response']
    if not status:
        print("some thing error when getting the page, status not ok")

    return tool.parse(text, 'benchmark')

def test_mode(url:str, tool:PwcTools, mode):
    # https://paperswithcode.com/sota/open-vocabulary-object-detection-on-lvis-v1-0
    paper_url = 'https://paperswithcode.com' + url if url.startswith('/') else url
    save_file_path = f"cache2/{mode}/search#{url.replace('/','#').replace('.','*')}.html"
    res = get_page_v2(paper_url,save_file_path)       # 
    text, status, response = res['text'], res['status_ok'], res['response']
    if not status:
        print("some thing error when getting the page, status not ok")

    return tool.parse(text, mode)




if __name__=='__main__':
    tool = PwcTools

    # res = tool.parse('ok','query')
    # print(res)

    # test_query(query='open-vocabulary',tool=tool)       # 正常搜索页面
    # test_query(query='object detection',tool=tool)      # 搜索跳转到 task、paper 页面等情形
    # test_query(query='asvv dsvd',tool=tool)             # 没有结果

    # test_paper(url='/paper/zero-shot-detection-via-vision-and-language',tool=tool)
    # test_paper(url='https://paperswithcode.com/paper/modeling-with-recurrent-neural-networks-for',tool=tool)


    # test_benchmark(url='https://paperswithcode.com/sota/semantic-segmentation-on-ade20k',tool=tool)
    # test_benchmark(url='https://paperswithcode.com/sota/open-vocabulary-object-detection-on-lvis-v1-0',tool=tool)

    # test_mode(url='https://paperswithcode.com/dataset/lvis',tool=tool,mode='dataset')
    # test_mode(url='https://paperswithcode.com/dataset/ade20k',tool=tool,mode='dataset')

    # test_mode(url='https://paperswithcode.com/task/object-detection',tool=tool,mode='task')
    # test_mode(url='https://paperswithcode.com/task/aerial-video-semantic-segmentation',tool=tool,mode='task')

    # test_mode(url='https://paperswithcode.com/method/average-pooling',tool=tool,mode='method')
    # test_mode(url='https://paperswithcode.com/method/resnet',tool=tool,mode='method')






