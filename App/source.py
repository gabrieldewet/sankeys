from tkmodule import App, ProgBar
import process
from html_py import gen_html
import clean
import get_json
import tkinter as Tk

# Create App:
app = App()
app.mainloop()

sfiles = app.start_out['Studentfiles']  # Student files
pfiles = app.start_out['Planfiles']  # Plan files (not really used outside of app)
uplans = app.start_out['uPlans']  # Only use if plans & codes == "All"
plans_desc1 = dict(zip(uplans["b"], uplans["a"]))  # codes:plans for all undergrad programs starting with "B"
dict_all = app.start_out['aPlans']  # All codes:plans for years of files selected
mg_dict = app.start_out['mingrad']

ystart = int(app.next_out["ystart"])  # Start year of files
plans = [app.next_out["pname"]]  # Selected academic plan name

if plans[0] == "All":
    codes = [app.next_out["pcode"]]  # Selected academic plan code
else:
    codes = [int(app.next_out["pcode"])]  # Selected academic plan code

plans_desc2 = dict(zip(codes, plans))  # Selected code:plan dictionary
cohort = int(app.next_out["cohort"])  # Cohort year
saveloc = app.next_out["saveloc"]  # Save location, ultimately for HTML's

# If plans & codes == "All":
if plans[0] == "All":
    plans_desc = plans_desc1
else:
    plans_desc = plans_desc2

# Creat df's to be filtered:
filelist = sfiles  # Student files
years = [str(ystart + x) for x in range(len(filelist))]  # For which years files are used
codes_dict = dict_all  # All codes:plans for all years worth of files
master_ = process.get_master(filelist, years)  # Generate master dataframe containing all data for all students

pbar = ProgBar()

i = 1
for k, p in plans_desc.items():

    pbar.pvar.set(i / len(list(plans_desc.values())) * 100)
    pbar.update()
    # Get raw data frame containing all student data for plan p (code k)
    df_raw = process.get_plan(k, master_, cohort, int(mg_dict[k]), codes_dict)

    # Check if any data in df, then continue: (Maybe change to check if multiple "terms" in df
    if len(df_raw) > 10:
        df_clean = clean.clean_data(df_raw, cohort, int(years[-1]))

        newname = p.replace(":", " ").replace(" ", "_")
        name = "{0}_{1}".format(str(cohort), newname)

        gen_html(get_json.get(df_clean), name, saveloc)

    if int(pbar.pvar.get()) == 100:
        pbar.button.config(state="normal", command=pbar.finish_button)

    i += 1

pbar.mainloop()

