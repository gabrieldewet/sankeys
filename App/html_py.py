import io
import pandas as pd


def get_html(nodes, links, filename, s_loc):

    base_html = io.open("base.html", mode="r", encoding="utf-8").read()
    base_html = base_html % (links, nodes)
    html_str = """{}""".format(base_html)
    file = open("{0}/{1}.html".format(s_loc, filename), "w")
    file.write(html_str)
    file.close


def gen_html(jfile, fname, save_loc):

    df_nodes = pd.DataFrame(jfile["nodes"])
    df_nodes.columns = ["name"]
    df_nodes["name"] = df_nodes["name"].str[1:]

    df_links = pd.DataFrame(jfile["links"])
    df_links.rename(columns={'weight': 'value'}, inplace=True)

    get_html(df_nodes.to_json(orient="records"), df_links.to_json(orient="records"), fname, save_loc)
