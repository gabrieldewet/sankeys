import pandas as pd

# ======================================================================================================================
# Import flat files and filter filter filter
#  Fields  #  Columns  #
########################
# Stu Num  #  (0,15)   #
# Qualcode #  (30,45)  #
# Commence #  (45,53)  #
# Require  #  (88,89)  #
# ======================================================================================================================
# Define necessary functions


def n_years(row):  # Number of years a student has been in a particular programme
    if int(str(row["Commencement"])[4:6]) >= 5:
        yr = int(str(row["Commencement"])[0:4]) + 1
    else:
        yr = int(str(row["Commencement"])[0:4])
    return 1 + int(row["Term"]) - yr


def func(row, dct):  # Function to return plan name from dict
    return dct[row["QualiCode"]]


def get_master(files, year):
    colnames = ["Student Number", "QualiCode", "Commencement", "Quali. Status"]
    cols = [(0, 15), (30, 45), (45, 53), (88, 89)]
    all_df = {y: pd.read_fwf("{}".format(f), colspecs=cols,
                             names=colnames) for y, f in zip(year, files)}

    mast = pd.DataFrame()
    for y in year:
        all_df[y].dropna(axis=0, subset=["Commencement"], inplace=True)
        all_df[y].sort_values(['Student Number', 'Commencement'], inplace=True)
        all_df[y].drop_duplicates(["Student Number"], inplace=True)
        all_df[y]["Term"] = int(y)
        mast = mast.append(all_df[y], ignore_index=True)

    mast["Number of Years"] = mast.apply(lambda row: n_years(row), axis=1)
    return mast


def get_plan(key, master, cort, mingrad, code_dict):
    mapfunc = master["Quali. Status"].map(lambda x: x == "F")

    sns_fy = master.loc[(master["QualiCode"] == int(key)) &
                        (master["Term"] == cort), "Student Number"]  # Get initial snumbers to compare to early grads

    sns_eg = pd.Series()  # Early grads, take 'em out
    for i in range(mingrad-1):
        sns_i = master.loc[(master["Student Number"].isin(sns_fy)) &
                           (master["Term"] == cort + i) &
                           mapfunc, "Student Number"]
        sns_eg = sns_eg.append(sns_i)

    sns = master.loc[(~master["Student Number"].isin(sns_eg)) &
                     (master["QualiCode"] == int(key)) &
                     (master["Number of Years"] == 1) &
                     (master["Term"] == cort), "Student Number"]

    if len(sns) > 0:
        temp = master.loc[(master["Student Number"].isin(sns)) &
                          (master["Term"].astype(int) >= int(cort)), :].copy()
        temp["Plan Desc"] = temp["QualiCode"].apply(lambda row: code_dict[row])
        keepcol = ["Student Number", "Term", "Quali. Status", "Plan Desc", "Number of Years"]

        return temp.loc[:, keepcol]

    else:
        return pd.DataFrame()
