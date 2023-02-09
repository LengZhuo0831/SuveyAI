from pyecharts import options as opts
from pyecharts.charts import Tree
try:
    from request_pwc import PwcTools, test_mode
except:
    from .request_pwc import PwcTools, test_mode


def transform_data(data, depth=0):
    if isinstance(data,(list,tuple)):
        if depth==0:
            return {
                "children":[{"name":i, "children":transform_data(item, depth+1)} for i, item in enumerate(data)],
                "name":"root",
                "value":len(data)
            }
        else:
            return [{"name":i, "children":transform_data(item, depth+1),"value":len(data)} for i, item in enumerate(data)]
    
    elif isinstance(data,dict):
        if depth==0:
            return {
                "children":[{"name":key, "children":transform_data(item, depth+1)} for key, item in data.items()],
                "name":"root",
                "value":len(data)
            }
        else:
            return [{"name":key, "children":transform_data(item, depth+1),"value":len(data)} for key, item in data.items()]
    
    else:
        if depth==0:
            return {
                "children":[{"name":str(data)}],
                "name":"root"
            }
        else:
            return [{"name":str(data)}]

if __name__=='__main__':
    data = [transform_data(test_mode(url='https://paperswithcode.com/dataset/lvis',tool=PwcTools,mode='dataset'))]
    c = (
        Tree(init_opts=opts.InitOpts(
            width='1600px',
            height='900px',
            page_title='lz_tree',
        ))
        .add(
            series_name="", 
            data=data,
            pos_top='10%',
            pos_left='8%',
            pos_bottom='22%',
            pos_right='20%',
            edge_shape='polyline',
            edge_fork_position='63%',
            initial_tree_depth=4,
            collapse_interval=1,
            label_opts=dict(position='right',horizontal_align='left'),
            leaves_label_opts=dict(position='right',horizontal_align='left'),
            tooltip_opts=opts.TooltipOpts(),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Tree"),
            datazoom_opts=opts.DataZoomOpts(),
            )
        .render("cache2/tree.html")
    )
