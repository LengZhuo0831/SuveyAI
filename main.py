import sys

def main():
    args = sys.argv
    # print(args)
    if len(args)==1:
        # 没有任何参数
        print("No command? Need help? Read the Readme.md or try run:\n python main.py help")
        return
    command = args[1]
    if command=='help':
        print('''
        你可以在 python main.py 后接如下命令：
        creat [project name] 创建一个爬虫项目

        解析 query 及其他页面：
        parse_query [project name] [query or queries(空格隔开)]
        parse [project name] query [query or queries(空格隔开)]
        parse [project name] [mode] [url or urls], mode: 'paper', 'benchmark', 'dataset', 'task', 'method'.

        如果你准备好了一个 query list 或者 urls list，保存在文档中，也可以用下面的命令：
        parse_list_query [project name] [path of query list file]
        parse_list [project name] query [path of query list file]
        parse_list [project name] [mode] [path of url list file], mode: 'paper', 'benchmark', 'dataset', 'task', 'method'.

        想要保存成 excel：
        to_excel [project name] [save file path]

        深层爬取：
        

        你需要知道每个页面解析后会返回的内容？请参考 Readme.md
        
        ''')



main()



