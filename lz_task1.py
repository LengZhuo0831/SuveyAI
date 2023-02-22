from PapersProject import *
from tqdm import tqdm

def main1():
    p = PaperProject('Attack')
    p.load()
    queries = [
        'adverserial attack',
        'adeverserial attack against object detector',
        'attack object detector',
        'attact for object detection',
        'defence object detector',
        'guard object detector',
        'Robust object detection',
        'Robust detection',
        'Adversarial Robustness',
        'Adversarial Attack'
    ]
    for q in queries:
        p.parse_query(q)

    p.save()

# main1()
    
def main2():
    task_urls = [
        'https://paperswithcode.com/task/adversarial-robustness',
        'https://paperswithcode.com/task/adversarial-attack'
    ]
    p = PaperProject('Attack')
    p.load()

    for url in task_urls:
        p.parse_mode(url)
    p.save()

    return


# main2()

def main3():
    p = PaperProject('Attack')
    p.load()
    urls = p.get_paperurl_from_tasks()
    urls.extend(p.get_paperurl_from_queries())
    urls = set(urls)
    for url in urls:
        try:
            p.parse_mode(url)
        except:
            continue
    p.save()
    return

# main3()

def main4():
    p = PaperProject('Attack')
    p.load()
    res = dict()
    key1 = ['detector','detection','rcnn','yolo']
    key2 = ['defence','defend','secure','security','robust','vulnerability','adverserial','attack']
    for k, paper in tqdm(p.papers.items()):
        paper_title = paper['paper_title']
        abstract = paper['abstract']
        for k1 in key1:
            if k1 in paper_title.lower() or k1 in abstract.lower():
                for k2 in key2:
                    if k2 in paper_title.lower() or k1 in abstract.lower():
                        res[k]=paper

    p.papers = res

    p.to_excel()

# main4()
'''
Explaining and harnessing adversarial examples
Adversarial patch
Dpatch: An adversarial patch attack on object detectors
On physical adversarial patches for object detection

Robust and accurate object detection via adversarial learning
Making an invisibility cloak: Real world adversarial attacks on object detectors
Segment and Complete: Defending Object Detectors against Adversarial Patch Attacks with Robust Patch Detection

'''
