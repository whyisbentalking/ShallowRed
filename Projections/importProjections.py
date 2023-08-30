
import pandas as pd
import numpy as np
import tabula 

def importPDFProjections():
    tabula.convert_into(f"E:\\Ben\\Documents\\ShallowRed\\Projections\\NFLDK2023_CS_ClayProjections2023.pdf","Projections\\Qb-projections.csv",output_format="csv",pages="35")
    tabula.convert_into(f"E:\\Ben\\Documents\\ShallowRed\\Projections\\NFLDK2023_CS_ClayProjections2023.pdf","Projections\\Rb-projections.csv",output_format="csv",pages="36-38")
    tabula.convert_into(f"E:\\Ben\\Documents\\ShallowRed\\Projections\\NFLDK2023_CS_ClayProjections2023.pdf","Projections\\Wr-projections.csv",output_format="csv",pages="39-43")
    tabula.convert_into(f"E:\\Ben\\Documents\\ShallowRed\\Projections\\NFLDK2023_CS_ClayProjections2023.pdf","Projections\\Te-projections.csv",output_format="csv",pages="44,45")
    return

def get_Projections():
    qb = pd.read_csv("Projections\\Qb-projections.csv")
    rb = pd.read_csv("Projections\\Rb-projections.csv")
    wr = pd.read_csv("Projections\\Wr-projections.csv")
    te = pd.read_csv("Projections\\Te-projections.csv")
    d = pd.read_csv("Projections\\D-projections.csv")
    k = pd.read_csv("Projections\\K-projections.csv")

    df = pd.concat([qb,rb,wr,te,d,k],ignore_index=True)

    df.to_csv("Projections\\combined-projections.csv")
    return df

def main():
    df = get_Projections()


if __name__ == '__main__':
    main()