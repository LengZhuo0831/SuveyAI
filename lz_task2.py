papers = '''
Explaining and harnessing adversarial examples.
Towards deep learning models resistant to adversarial attacks.
Adversarial examples for semantic segmentation and object detection.
Transferable adversarial attacks for image and video object detection.
DPATCH: an adversarial patch attack on object detectors.

Ensemble adversarial training: Attacks and defenses.
Towards evaluating the robustness of neural networks.
Defense against adversarial attacks using high-level representation guided denoiser.
Attacks which do not kill training make adversarial learning stronger.
Adversarial robustness through local linearization.
Towards adversarially robust object detection.
Class-aware robust adversarial training for object detection.

Adversarial Examples for Object Detection.
Object Detection under Adversarial Conditions.
Adversarial Attacks and Defenses in Images, Graphs and Text: A Review.
Defense Against Adversarial Attacks Using High-Level Representation Guided Denoiser.
'''

'''
Object Detection under Adversarial Conditions.
Towards adversarially robust object detection.
'''
from PapersProject import *
from utils.google_util import GoogleUtil
from tqdm import tqdm

def main1():
    proj = PaperProject('attack2')
    proj.save()
    queries = papers.split('\n')
    for query in queries:
        if query=='':
            continue
        print(query)
        proj.parse_query(query, 1)
    proj.save()

    return
# main1()

def main2():
    proj = PaperProject('attack2')
    proj.load()
    urls = proj.get_paperurl_from_queries()
    for url in urls:
        try:
            proj.parse_mode(url)
        except:
            continue
    proj.save()
    proj.to_excel()
    return
# main2()


papers2 = '''
Explaining and Harnessing Adversarial Examples
Towards Deep Learning Models Resistant to Adversarial Attacks
Adversarial Examples for Semantic Segmentation and Object Detection
Regional Homogeneity: Towards Learning Transferable Universal Adversarial Perturbations Against Defenses
Evaluating the Robustness of Semantic Segmentation for Autonomous Driving against Real-World Adversarial Patch Attacks
Transferable Adversarial Attacks for Image and Video Object Detection
Object Hider: Adversarial Patch Attack Against Object Detectors
DPatch: An Adversarial Patch Attack on Object Detectors
Ensemble Adversarial Training: Attacks and Defenses
RobustBench: a standardized adversarial robustness benchmark
Boosting Adversarial Attacks with Momentum
Defense against Adversarial Attacks Using High-Level Representation Guided Denoiser
Shield: Fast, Practical Defense and Vaccination for Deep Learning using JPEG Compression
A Self-supervised Approach for Adversarial Robustness
Towards Evaluating the Robustness of Neural Networks
Is Robustness the Cost of Accuracy? -- A Comprehensive Study on the Robustness of 18 Deep Image Classification Models
Towards Adversarially Robust Object Detection
Class-Aware Robust Adversarial Training for Object Detection
Robust and Accurate Object Detection via Adversarial Learning
Adversarial Camouflage: Hiding Physical-World Attacks with Natural Styles
APRICOT: A Dataset of Physical Adversarial Attacks on Object Detection
Adversarial Attacks and Defenses in Images, Graphs and Text: A Review
'''
def main3():
    util = GoogleUtil()
    qs = papers2.split('\n')
    res_all = dict()
    for q in qs:
        if q=='':
            continue
        res = util.parse_paper(paper_name=q)
        res_all[q] = res
    proj = PaperProject('attack2')
    proj.load()
    proj.google_res = res_all
    proj.save()

    return
# main3()
