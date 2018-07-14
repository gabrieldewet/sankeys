import io
import pandas as pd


def get_html(base,nodes, links, mod, cort, d3, s_loc, mult):
    base_html = io.open(base, mode="r", encoding="utf-8").read()
    if mult:
        base_html = base_html % (mod,cort,mod,d3,links,nodes)
        file = io.open("{0}/{1}_{2}_color.html".format(s_loc, mod, cort), "w", encoding="utf-8")
    else:
        base_html = base_html % (mod,cort,d3,links,nodes)
        file = io.open("{0}/{1}_{2}.html".format(s_loc, mod, cort), "w", encoding="utf-8")
    html_str = """{}""".format(base_html)
    file.write(html_str)
    file.close


def gen_html(base,jfile, mod, cort, d3, save_loc, multi=False):

    df_nodes = pd.DataFrame(jfile["nodes"])
    df_nodes.columns = ["name"]
    df_nodes["name"] = df_nodes["name"].str[1:]

    df_links = pd.DataFrame(jfile["links"])
    df_links.rename(columns={'weight': 'value'}, inplace=True)

    get_html(base,df_nodes.to_json(orient="records"), df_links.to_json(orient="records"), 
             mod, cort, d3, save_loc, multi)
