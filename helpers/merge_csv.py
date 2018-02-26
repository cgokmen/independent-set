import os
import pandas

def merge_csv(p):
    dir_list = next(os.walk(p))[1]

    dataframes = []
    for dir in dir_list:
        csv = os.path.join(p, dir, "metrics.csv")
        df = pandas.read_csv(csv, ";", index_col=0)

        df_relevant = df[[df.columns[0],'Homogeneous neighborhoods']]

