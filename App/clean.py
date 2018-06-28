import pandas as pd

def node_col(row, ref):
    if row["Quali. Status"] == "F":
        return "Graduated"
    elif row["Plan Desc"] in ref:
        return row["Plan Desc"]
    else:
        return "Other"


def clean_data(df, start, end):
    dis_sns = df.loc[(df["Term"] > start), "Student Number"]
    dfd = df.loc[(~df["Student Number"].isin(dis_sns))].copy()
    dfd["Term"] = dfd["Term"].astype(int) + 1

    dfd1 = pd.DataFrame()
    for yr in range(start, end):
        dis_sns1 = df.loc[(df["Term"] > yr), "Student Number"]
        dfd11 = df.loc[(~df["Student Number"].isin(dis_sns1)) & (df["Term"] <= yr)].copy()
        dfd11["Term"] = yr + 1
        dfd11["Node Column"] = "Out"
        dfd1 = dfd1.append(dfd11).drop_duplicates(["Term", "Student Number"])

    # Step 4: Rename entries in original df so that df1 can be added:
    x = 10
    program_counts = pd.DataFrame(df["Plan Desc"].value_counts(), index=None)
    topx = program_counts.sort_values("Plan Desc", ascending=True)\
                         .iloc[-x:len(program_counts) + 1, ]
    topx = list(topx.index.values)
    #    print(topx)

    #    Different reference:
    df["Node Column"] = df.apply(lambda row: node_col(row, topx), axis=1)

    # Step 5: Combine df & df1 for plotting of sankey:
    df_out = df.append(df.append(dfd1)).sort_values(["Term", "Student Number", "Node Column"])

    return df_out.loc[df_out["Student Number"].shift(1) != df_out["Student Number"]]
