
# 下面介绍如何使用这个工具
I'll show you how to use this robot:  
## introduction
本代码仓主要爬取 paper with code 上的内容，包括基于 query 搜索，爬取 paper页面、benchmark页面、dataset页面、task页面和 method页面主要内容。  

### request_utils.py
主要提供接口：get_page_v2(url, save_file_path="", justText=True)，可以爬取 url 指定的网页源码，保存到 save_file_path，默认不保存。当然如果本地已经存在 save_file_path 文件，将直接读取该文件而非爬取，以减少对服务器的访问  

### request_pwc.py
主要实现了 PwcTools 这个类，它核心工作是将 get_page_v2 爬取的网页源码进行解析，分析出所需的主要内容，不同的页面均实现了解析，包括 query搜索页面、paper页面、benchmark 页面、dataset 页面、task 页面和 method 页面。并且可以使用统一的接口访问：parse(html, mode, **kwargs)，其中 mode 可选项为： ['query', 'paper', 'benchmark', 'dataset', 'task', 'method']，html为源代码文本。
parse方法根据mode指定的模式去调用相应的方法：  
- parce_query(html, **kwargs) - 解析 query 搜索页面  
- parce_paper(html, **kwargs) - 解析 paper 页面  
- parce_benchmark(html, **kwargs) - 解析 benchmark 页面  
- parce_dataset(html, **kwargs) - 解析 dataset 页面  
- parce_task(html, **kwargs) - 解析 task 页面  
- parce_method(html, **kwargs) - 解析 method 页面  

#### 返回字段：
这里介绍先简单列下每个函数的返回字段及类型，具体请客官们自行探索
~~~
# paese_query
dict(
    page_title=,
    page_url=,
    results=list_of_dict(
        dict(
            paper_name = ,
            paper_url = ,
            code_info = ,
            date_info = ,
            conference_info = ,
            other_info = ,
            strip_abstract = ,
            tasks = ,
            star = ,
            paper_url2 = 
        )
    )
)

# parse paper
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

# parse benchmark
return sota_list        # 我也还没细看

# parse dataset
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

# parse task
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

# parse method
return dict(
    method_title=method_title,
    method_info=method_info,
    method_paper_name=method_paper_name,
    method_paper_url=method_paper_url,
    components=components,
    category=category
)

~~~

#### 当你获取到相应的 url，可以这样去使用：
~~~
# replace by you self:
url = 'https://paperswithcode.com/dataset/cifar-10'
save_file_path = 'cifar-10.html'
mode = 'dataset' 

# get the page and parce it
from utils.request_utils import get_page_v2
from utils.request_pwc import PwcTools

res = get_page_v2(url, save_file_path)
text, status, response = res['text'], res['status_ok'], res['response']
if not status:
    print("some thing error when getting the page, status not ok")
res = PwcTools.parse(text, mode)

# you can use res as your will
for k, v in res.items():
    print(k,v)
~~~

### PaperProject.py
它假定了一个调研项目，并管理它，是最直接可调用的接口.(目前还在写)
它将保存你爬取的内容，并且可以调用save()接口存储下来，或者调用load()接口读取；还可以调用toexecl()存储为表格。

~~~
# 存
from PapersProject import PaperProject

project = PaperProject('Attention is all you need')
project.parse_query('Attention is all you need')
project.save()
~~~
~~~
# 取
project = PaperProject('Attention is all you need')
project.load()
~~~

## TODO:
目前正在完善功能，将在 main.py 中包装一些命令，从而更灵活的使用该工具。  
对于一些简单的功能，您可以自行编写 python 脚本完成。

## About
作者：冷焯  
邮箱：len@stu.pku.edu.cn




