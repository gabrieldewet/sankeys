""" Main script for generating Sankey Diagrams """
import clean
import get_json
import get_json2
from html_py import gen_html
import os

d3s = {"Online": "http://d3js.org/d3.v3.min.js", "Offline": "d3.min.js"}
modules = ["CMY 127"] 
#modules = ["CMY 382", "CMY 383", "CMY 384", "CMY 385"]
chorts = [2011,2012,2013,2014,2015]
show_plans = ['Chemistry', 'Microbiology', 'Biochemistry', 
              'Physics', 'Geology', 'Medical', 
              'Biological', 'Human Physiology', 
              'Genetics', 'Veterinary Science']

names = ["Marks", "Plans", "Students"]
file_names = {name: ["../Data/{0}/{1}".format(name, f) for f in
              os.listdir('../Data/{0}'.format(name))] for
              name in names}

plans = clean.read_plan(file_names["Plans"])

for chort in chorts: 
    sn, marks = clean.read_marks(file_names["Marks"], modules, chort, True)
    df = clean.read_student(file_names["Students"], 
                            chort, sn, plans, marks)
    dfnew = clean.clean_data(df, show_plans, 15)
    
    for key, val in d3s.items():
        gen_html("base_bl.html",get_json.get(dfnew), modules[0], str(chort), val, 
                 "../Output/Dark/{}".format(key))
        gen_html("base_mbl.html",get_json2.get(dfnew), modules[0], str(chort), val, 
                 "../Output/Dark/{}".format(key), True)


