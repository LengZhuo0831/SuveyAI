
from utils import PwcTools, get_page_v2
import os
import pickle as pkl
import json

import xlsxwriter

class PaperProject():
    def __init__(self, name) -> None:
        # assert not os.path.exists(os.path.join('projects',name))
        try:
            os.mkdir(os.path.join('projects',name))
            os.mkdir(os.path.join('projects',name,'cache'))
            for dirr in ['query', 'paper', 'benchmark', 'dataset', 'task', 'method']:
                os.mkdir(os.path.join('projects',name,'cache',dirr))
        except:
            pass

        self.name = name
        self.path = os.path.join('projects',name)
        self.queries = dict()
        self.papers = dict()
        self.benchmarks = dict()
        self.datasets = dict()
        self.tasks = dict()
        self.methods = dict()

        self.tool = PwcTools

        
        

    def add_paper(self,paper):
        assert 'paper_name' in paper
        if paper['paper_name'] in self.papers:
            return False
        else:
            self.papers[paper['paper_name']]=paper
            return True
    
    def add_query_paper(self, paper, query):
        assert 'paper_name' in paper
        if paper['paper_name'] in self.papers:
            return False
        else:
            self.queries[query][paper['paper_name']]=paper
            return True

    def parse_query(self, query, max_page_num=5):
        assert '/' not in query
        all_count=0
        self.queries[query]=dict()
        for i in range(max_page_num):
            url = f"https://paperswithcode.com/search?q_meta=&q_type=&q={query}&page={i+1}"
            save_file_path = os.path.join(self.path,'cache','query',f'{query}_page{i+1}.html')
            res = get_page_v2(url, save_file_path)       # 
            text, status, response = res['text'], res['status_ok'], res['response']
            if not status:
                print("some thing error when getting the page, status not ok")

            papers = self.tool.parse(text, 'query')
            page_url = papers['page_url']
            if 'search' not in page_url:
                print(f"the page url changed to {page_url}")
                break
            results = papers['results']
            if len(results)==0:
                break
            flag = True
            global_flag = True
            count = 0
            for paper in results:
                paper_name = paper['paper_name']
                print(f'adding paper: {paper_name}')
                flag = self.add_query_paper(paper, query)
                if flag:
                    count+=1
                else:
                    global_flag=False
            print(f"======== Added {count} paper in page {i+1}")
            all_count+=count
            if not global_flag:
                # 说明存在部分paper在上一页就存在，可以不用继续往后搜索
                break
        print(f"============= Summary =============\nSearch query: {query}\nAdded papers num:{all_count}")

    def parse_mode(self, url):
        page_url = 'https://paperswithcode.com' + url if url.startswith('/') else url
        mode = page_url.split('/')[3]
        if mode=='sota':
            mode='benchmark'
        save_file_path = os.path.join(self.path,'cache',mode,f"{page_url.replace('/','#').replace('.','*')}.html")
        
        res = get_page_v2(page_url, save_file_path)
        text, status, response = res['text'], res['status_ok'], res['response']
        if not status:
            print("some thing error when getting the page, status not ok")
        
        # 在
        res = self.tool.parse(text, mode, MAX_PAGE=10, sort_mode='greatest', save_root=os.path.join(self.path,'cache'))
        save_map=dict(query=self.queries, paper=self.papers, benchmark=self.benchmarks, dataset=self.datasets, task=self.tasks, method=self.methods)
        save_map[mode][page_url]=res



    def save(self, mode='json'):
        assert mode in ['json']
        if mode=='pkl':
            pass
            # pkl.dump(self, open(os.path.join(self.path,self.name+'.pkl'),'wb'))
        elif mode=='json':
            json.dump(dict(
                name = self.name,
                path = self.path,
                queries = self.queries,
                papers = self.papers,
                benchmarks = self.benchmarks,
                datasets = self.datasets,
                tasks = self.tasks,
                methods = self.methods
            ),open(os.path.join(self.path,self.name+'.json'),'w'))

        
    def load(self, file:str='default', mode='write'):
        assert mode in ['write','merge']
        if file=='default':
            file = os.path.join(self.path, self.name+'.json')
        if file.endswith('json'):
            res = json.load(open(file,'r'))
            if mode=='write':
                self.name = res['name']
                self.path = res['path']
                self.queries = res['queries']
                self.papers = res['papers']
                self.benchmarks = res['benchmarks']
                self.datasets = res['datasets']
                self.tasks = res['tasks']
                self.methods = res['methods']
            elif mode=='merge':
                self.queries.update(res['queries'])
                self.papers.update(res['papers'])
                self.benchmarks.update(res['benchmarks'])
                self.datasets.update(res['datasets'])
                self.tasks.update(res['tasks'])
                self.methods.update(res['methods'])
        elif file.endswith('pkl'):
            if mode=='write':
                self=pkl.load(open(os.path.join(self.path,self.name+'.pkl'),'rb'))
            elif mode=='merge':
                project = pkl.load(open(os.path.join(self.path,self.name+'.pkl'),'rb'))
                self.queries.update(project.queries)
                self.papers.update(project.papers)
                self.benchmarks.update(project.benchmarks)
                self.datasets.update(project.datasets)
                self.tasks.update(project.tasks)
                self.methods.update(project.methods)

    def toexecl(self):
        save_excel = os.path.join(self.path,f"{self.name}.xlsx")
        wbook = xlsxwriter.Workbook(save_excel)
        wsheet = wbook.add_worksheet('papers')
        heads = ['title','paper url','code','star','authors','conference','date','abstract','datasets']
        wsheet.write_row(row=0,col=1,data=heads)
        for ii, (k, paper) in enumerate(self.papers.items()):
            title = paper['paper_title']
            url = '' if len(paper['paper_urls'])==0 else paper['paper_urls'][0]
            code = '' if len(paper['code_lst'])==0 else paper['code_lst'][0][0]
            star = '' if len(paper['code_lst'])==0 else paper['code_lst'][0][1]
            abstract = paper['abstract']
            authors = ''
            for au in paper['authors']:
                authors+=au+'\n'
            authors=authors[:-1]
            date = paper['date']
            conference = paper['conference_info']
            datasets=''
            for d in paper['datasets_lst']:
                datasets+=d[1]+'\n'
            datasets=datasets[:-1]
            wsheet.write_row(row=ii+1,col=1,data=(title,url,code,star,authors,conference,date,abstract,datasets))


        print(f"saving {save_excel}")
        wbook.close()





if __name__=='__main__':
    queries = [
        'continual object detection',
        'incremental learning for object detection',
        'incremental learning',
        'continual learning'
        ]
    project = PaperProject('glip4det-continual-OD')
    # for q in queries:
    #     print(f'\n======================================== Serching query {q} ========================================')
    #     project.parse_query(q)
    # # project.save()
    # project.save('json')

    # # project.load('default')
    # project.parse_mode('https://paperswithcode.com/task/continual-learning')
    # project.parse_mode('https://paperswithcode.com/task/incremental-learning')

    # # project.save()
    # project.save('json')


    

    # project = PaperProject('glip4det-continual-OD')
    # project.load('default')
    # project.save()

    # for k, tasks in project.tasks.items():
    #     for benchmark in tasks['benchmark_lst']:
    #         url = benchmark['Dataset'][0]
    #         project.parse_mode(url)
    # project.save()

    project.load()
    # for k, tasks in project.tasks.items():
    #     for paper in tasks['paper_lst']:
    #         url = paper['paper_url']
    #         project.parse_mode(url)
    # project.save()

    project.toexecl()
    print('exit...')
