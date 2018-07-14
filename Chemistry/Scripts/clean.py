"""  Clean data and pull required student records """

import pandas as pd


# Functions to read plan flatfiles:
def read_plan(files):

    cols = [(0,15),(106,171),(98, 99)]
    colnames = ["QualiCode","Academic Plan","MinGrad"]

    mast = pd.DataFrame()
    for f in files:
        temp_df = pd.read_fwf(f, colspecs=cols, names=colnames)
        mast = mast.append(temp_df.drop_duplicates(["QualiCode"]))
        
    pdict = dict(zip(mast["QualiCode"], 
                 zip(mast["Academic Plan"],mast["MinGrad"])))

    return pdict


# Function for reading csv's
def read_marks(files, mods, cohort, get_marks):
    """
    :param files: location of mark files
    :param mods: list of modules to be included
    :param cohort: cohort of interest
    :param get_marks: return marks (boolean)
    :return: dict containing student numbers, df
    """
    df = pd.DataFrame()
    for f in files:
        temp_df = pd.read_csv(f, sep=';')
        df = df.append(temp_df)

    # Year of module
    mody = int(str(mods[0])[4]) - 1
    
    # Get students that deregistered for mod in current year
    sn_nr = df.loc[(df["Term"] == (cohort + mody)) &
                   (df["Course Code"].isin(mods)),"Student Number"]

    # Get student numbers of students registered for specified modules
    sn = df.loc[(df["Course Code"].isin(mods)) &
                (df["Final Mark"].notna()) &
                (df["Student Number"].isin(sn_nr)), "Student Number"]
                
#    sn = df.loc[(df["Course Code"].isin(mods)) &
#                ( (df["Final Mark"].notna()) & 
#                  (df["Semester Mark"]).notna()), "Student Number"]
                
    
    
    # Bool series of students who have >1st year mods in 1st year
    mapfunc = df["Course Code"].map(lambda x: int(str(x)[4]) != 1)

    # Get stud numbs of 1st years that are not registered for > 1st year mods
    snums = df.loc[(df["Term"] == cohort) &
                   mapfunc, "Student Number"]

    # Get final student numbers for cohort
    sn_out = df.loc[(~df["Student Number"].isin(snums)) &
                    (df["Student Number"].isin(sn)), "Student Number"].unique()

    if get_marks:
        # Get marks for specified module (return dict)
        marks_df = df.loc[(df["Student Number"].isin(sn_out)) &
                           (df["Course Code"].isin(mods)), :]
        marks_df = discretize(adjust_marks(marks_df))
        marks_dict = dict(zip(marks_df["Student Number"], marks_df["Final Mark"]))

        return sn_out, marks_dict


    else:
        return sn_out, False


# Function to filter out unwanted codes
def adjust_marks(df_in):
    # Use this function inside of read_marks function to return final df

    # Keep these columns:
    keep = ["Student Number", "Final Mark"]

    # To do:
    # 1) Drop nan final marks (deregistered)
    df = df_in.dropna(subset = ["Final Mark"]).copy()
#    df = df_in.dropna(subset = ["Final Mark", "Semester Mark"]).copy()

    # 3) For code 988, let final mark = min(semestermark/2;zero) (Not admitted)
    # 4) For code 987, let final mark = min(semestermark/2;zero) (Absent)
    # 5) For code 992, let final mark = min(semestermark/2;zero) (Exam too low)
    df["Final Mark"] = df.apply(lambda row: adj_codes(row), axis=1)

    # 6) Drop code 950 (Exemption exam passed) or discretize with rest
    # 7) Drop codes 995,984,977,985,976,989,967,981 (Unknown codes)
    to_drop = [950, 995, 984, 977, 985, 976, 989, 967, 981, 997, 996, 994]
    df = df.loc[~df["Final Mark"].isin(to_drop),:]
    
    df = df.sort_values(["Student Number","Final Mark"], ascending=False)\
           .drop_duplicates("Student Number").sort_index()

    df = df.reset_index()
    return df.loc[:,keep]


# Adjusts final marks with special codes
def adj_codes(row):
    if row["Final Mark"] in (988, 987, 992):
        return min([row["Semester Mark"],0])
    else:
        return row["Final Mark"]


# Function for discretization
def discretize(df):
    # Bins: [(0), (0<30), (30<50), (50<60), (60<75), (75<100), (NA)]
    bins = ["0", "0-29", "30-49", "50-59", "60-74", "75+"]
    vals = [-1,0,29,49,59,74,101]

    df["Final Mark"] = pd.cut(df["Final Mark"],vals,labels=bins)

    return df


# Number of years a student has been in a particular programme
def n_years(row):
    if int(str(row["Commencement"])[4:6]) >= 5:
        yr = int(str(row["Commencement"])[0:4]) + 1
    else:
        yr = int(str(row["Commencement"])[0:4])
    return 1 + int(row["Term"]) - yr


# Functions to read student flatfiles:
def read_student(files, cohort, students, code_dict, marks_):
    
    colors = {"0":"red", "0-29":"orange", "30-49":"yellow", "50-59":"green", "60-74":"blue", "75+":"purple"}
    cols = [(0,15),(30,45),(45,53),(88,89)]
    colnames = ["Student Number", "QualiCode", "Commencement", "Quali. Status"]
    years = ["2011", "2012", "2013", "2014", "2015", "2016", "2017"]
    mingrad = 3

    keepcol = ["Student Number", "Term", "Quali. Status",
               "PlanDesc", "Number of Years", "MinGrad"]

    df = pd.DataFrame()
    for y,f in zip(years, files):
        temp_df = pd.read_fwf(f, colspecs=cols, names=colnames)
        temp_df.sort_values(['Student Number', 'Commencement'], inplace=True)
        temp_df.drop_duplicates(["Student Number"], inplace=True)
        temp_df["Term"] = int(y)
        temp_df.dropna(subset=['Commencement'],inplace=True)
        df = df.append(temp_df, ignore_index=True)

    df["Number of Years"] = df.apply(lambda row: n_years(row), axis=1)

    # Lambda function for early grads removal
    mapfunc = df["Quali. Status"].map(lambda x: x == "F")

    # First year student numbers:
    sn_fy = df.loc[(df["Student Number"].isin(students)) &
                   (df["Term"] == cohort), "Student Number"]

    # Early grad student numbers
    sn_eg = pd.Series()
    for i in range(mingrad-1):
        sn_i = df.loc[(df["Student Number"].isin(sn_fy)) &
                       (df["Term"] == cohort + i) &
                       mapfunc, "Student Number"]

        sn_eg = sn_eg.append(sn_i)
        
    df["PlanDesc"] = df["QualiCode"].apply(lambda row: code_dict[row][0])
    df["MinGrad"] = df["QualiCode"].apply(lambda row: code_dict[row][1])

    # Get cohort student numbers
    sn = df.loc[(~df["Student Number"].isin(sn_eg)) &
                (df["Student Number"].isin(students)) &
                (df["Number of Years"] == 1) &
                (df["Term"] == cohort) &
                (df["MinGrad"] > 2), "Student Number"]
    
    df = df.loc[(df["Student Number"].isin(sn)) &
                (df["Term"].astype(int) >= int(cohort)),:]
    
    if marks_:
        df["Final Mark"] = df["Student Number"].apply(lambda row: marks_[row])
        
        for cat in df["Final Mark"].sort_values().unique(): 
            print(cat)
            df.loc[df["Final Mark"] == cat,"Group"] = colors[cat]
            
        keepcol.extend(["Final Mark", "Group"])
        return df.loc[:,keepcol]

    else:
        return df.loc[:,keepcol]
    
    
def clean_data(dfin, show = False, x =10):
    df = dfin.copy()
    start = min(df["Term"].unique())
    
    if show:
        topx = show
    
    else:
        #Rename entries in original df so that df1 can be added:
        program_counts = pd.DataFrame(df.loc[df["Term"] == start,"PlanDesc"]\
                                      .value_counts(), index=None)
    #    program_counts = pd.DataFrame(df["PlanDesc"].value_counts(), index=None)
        topx = program_counts.sort_values("PlanDesc", ascending=True)\
                             .iloc[-x:len(program_counts) + 1, ]
        topx = list(topx.index.values)

    #    Different reference:
    df["Node Column"] = df.apply(lambda row: node_col2(row, topx, start), axis=1)

    # Add out columns
    index = pd.MultiIndex.from_product(df.set_index(["Student Number","Term"]).index.levels, names = ["Student Number","Term"])
    df = df.set_index(["Student Number","Term"]).reindex(index).reset_index()
    df.loc[:,"Node Column"].fillna("Out",inplace=True)
    df.fillna(method="ffill",inplace = True)
        
    return df.sort_values(["Term", "Student Number", "Node Column"])
    
def node_col2(row, ref, sty):    
    
    
    # First, deal with possible postgrad outcomes
    if row["MinGrad"] == 1:
        
        if any(st in row["PlanDesc"] for st in ["BSc","MSc"]):
                    
            if row["Quali. Status"] == "F": 
                return row["PlanDesc"].split(':')[0][0:7] + " (G)"
            else:
                return row["PlanDesc"].split(':')[0][0:7]
            
#        if row["Quali. Status"] == "F": 
#            return row["PlanDesc"] + " (G)"
#        else:
#            return row["PlanDesc"]
    

        else:
            if row["Quali. Status"] == "F": 
                return "PostGrad (G)"
            else:
                return "PostGrad"
    
    elif row["Quali. Status"] == "F":
        return "Graduated"
    
    elif any(st in row["PlanDesc"] for st in ref):
        if row["Term"] < sty + 3:
            return row["PlanDesc"] #.split(':')[1] 
        else:
            return row["PlanDesc"].split(':')[0] 
    
    else:
        return "Other"
    