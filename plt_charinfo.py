"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""
from n_dist_keying.hocr_df_comparator import HocrDFComparator
from n_dist_keying.hocr_charinfo import get_charconfs, dump_charinfo, merge_charinfo
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def hocr2charinfo():
    # Get lists of Hocr-objects from testfiles
    hocr_comparator = HocrDFComparator()
    files = glob.iglob("/home/jkamlah/Coding/python_ocr/Testfiles/long/default/**/*.hocr", recursive=True)
    for file in files:
        if "ocro" in file:
            ocrolist = hocr_comparator.get_ocropus_df(file)
            ocro_charinfo = get_charconfs(ocrolist)
            dump_charinfo(ocro_charinfo, file[:-5] + "_charfons")

        # Charconfs processing
        if "tess" in file:
            tesslist = hocr_comparator.get_tesseract_df(file)
            tess_charinfo = get_charconfs(tesslist)
            dump_charinfo(tess_charinfo, file[:-5] + "_charfons")
    return 0

def plot_charinfo(charinfo,date,GROUPS=False,years=False,plot = "Histo"):
    # Plot Group
    if years:
        groupmembers = ["Zeichen", "Buchstaben", "Zahlen", "Satzzeichen"]
        for ocr in charinfo:
            for member in groupmembers:
                data = []
                labels = []
                for year in charinfo[ocr]:
                    labels.append(year)
                    data.append([float(x) for x in charinfo[ocr][year].get(member, {}).get("Confs", [])])
                output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
                bins_input = 10

                fileformat = ".png"

                # Plot
                sns.set()
                fig = plt.figure()
                ax = fig.add_subplot(111)
                bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=labels, showfliers=False)
                ax.set_title("Vergleich " + ocr +"_allYears_"+ member)
                ax.yaxis.grid(True)
                fig.tight_layout()
                plt.savefig(output + "compare_" + ocr +"_allYears_"+ member + fileformat)
                plt.close()
    elif GROUPS:
        groupmembers = ["Zeichen", "Buchstaben", "Zahlen", "Satzzeichen"]
        for ocr in charinfo:
            data = []
            for member in groupmembers:
                data.append([float(x) for x in charinfo[ocr].get(member, {}).get("Confs", [])])
            #data = ([float(x) for x in charinfosdict[ocr].get("Zeichen", {}).get("Confs", [])],
            #        [float(x) for x in charinfosdict[ocr].get("Buchstaben", {}).get("Confs", [])],
            #        [float(x) for x in charinfosdict[ocr].get("Zahlen", {}).get("Confs", [])],
            #        [float(x) for x in charinfosdict[ocr].get("Satzzeichen", {}).get("Confs", [])])
            # Settings
            output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
            bins_input = 10

            fileformat = ".png"

            # Plot
            sns.set()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            if plot == "Histo":
                # the histogram of the data
                # ax.hist(data, bins_input, histtype='bar',stacked=True)
                colors = ['red', 'tan', 'lime', 'blue']
                ax.hist(data, bins_input, density=True, histtype='bar', color=colors, label=groupmembers)
                plt.legend(loc='best')
                # label_patch = mpatches.Patch(color=, label=["Zeichen","Buchstaben","Zahlen","Satzzeichen"])
                # plt.legend(['red', 'tan', 'lime','blue'],["Zeichen","Buchstaben","Zahlen","Satzzeichen"])

            else:
                bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=groupmembers, showfliers=False)
                # plt.ylim((75, 100))
            ax.set_title("Vergleich "+ocr+date)
            ax.yaxis.grid(True)
            fig.tight_layout()
            plt.savefig(output + "compare_"+ocr+date +fileformat)
            plt.close()

    # Plot single Character
    else:
        for char in (charinfo["ocro"].keys() | charinfo["tess"].keys()):
            # Data
            data = ([float(x) for x in charinfo["ocro"].get(char, {}).get("Confs", [])],
                    [float(x) for x in charinfo["tess"].get(char, {}).get("Confs", [])])
            # Settings
            output = "/home/jkamlah/Coding/python_ocr/Testfiles/charconfs/figs/"
            bins_input = 10
            colors = ['red', 'lime']
            labels = ["Ocropus","Tesseract"]
            fileformat = ".png"

            # Plot
            sns.set()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plot = "Histo"
            if plot == "Histo":
                # the histogram of the data
                # ax.hist(data, bins_input, histtype='bar',stacked=True)
                ax.hist(data, bins_input, density=True, histtype='bar', color=colors, label=labels)
                plt.legend(loc='best')
                # label_patch = mpatches.Patch(color=, label=["Zeichen","Buchstaben","Zahlen","Satzzeichen"])
                # plt.legend(['red', 'tan', 'lime','blue'],["Zeichen","Buchstaben","Zahlen","Satzzeichen"])

            else:
                bplot1 = ax.boxplot(data, vert=True, patch_artist=True, labels=labels, showfliers=False)
                # plt.ylim((75, 100))
            ax.set_title("Vergleich von: "+char)
            ax.yaxis.grid(True)
            fig.tight_layout()
            plt.savefig(output + char + fileformat)
            plt.close()
    return 0

def charinfo_process(GROUPS = False):
    # Produce charinfo.json from hocr files

    hocr2charinfo()

    # Merge charinfo files
    years = glob.glob("/home/jkamlah/Coding/python_ocr/Testfiles/long/default/*")
    comparator = {"ocro":{},"tess":{}}
    for year in [years.sort()]:
        files = glob.glob(year+"/ocro/*.json", recursive=True)
        date = year.split("/")[-1]
        charinfo={"ocro":{},"tess":{}}
        charinfo["ocro"] = merge_charinfo(files,GROUPS)
        comparator["ocro"][date] = {}
        comparator["ocro"][date] = merge_charinfo(files,GROUPS)
        files = glob.glob(year+"/tess/*.json", recursive=True)
        charinfo["tess"] = merge_charinfo(files,GROUPS)
        comparator["tess"][date] = {}
        comparator["tess"][date] = merge_charinfo(files, GROUPS)

    #    # Try to implement pandas DF
    #    ocroarr   =   ["Ocropy"]*len(ocro_charinfo)
    #    ocrochar  =   list(ocro_charinfo.keys())
    #    ocromean  =   [statistics.mean(float(x) for x in ocro_charinfo[key]["Confs"]) for key in ocro_charinfo]
    #    tessarr   =   ["Tesseract"] * len(tess_charinfo)
    #    tesschar  =   list(tess_charinfo.keys())
    #    tessmean  =   [statistics.mean(float(x) for x in tess_charinfo[key]["Confs"]) for key in tess_charinfo]


    #    df = pd.DataFrame({"OCR":ocroarr+tessarr,"Char":ocrochar+tesschar,"Mean":ocromean+tessmean})

        plot_charinfo(charinfo,date,GROUPS)
        stop = "STOP"
    plot_charinfo(comparator, [], GROUPS=False,years=True)

if __name__=="__main__":
    charinfo_process(True)


def obsolete():
    sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
    rs = np.random.RandomState(1979)
    #x = rs.randn(500)
    df = pd.DataFrame({"Ocropus":[float(x) for x in ocro_charinfo.get(char,{}).get("Confs",[])],
                       "Tesseract":[float(x) for x in tess_charinfo.get(char,{}).get("Confs",[])]})
    df.plot()
    ts = df.cumsum()
    ts.plot()
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    sns.FacetGrid(df, aspect=15, size=.5, palette=pal)

    plt.show()
    stop = "STOP"



    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
    g = sns.FacetGrid(df, row="g", hue="g", aspect=15, size=.5, palette=pal)

    # Draw the densities in a few steps
    g.map(sns.kdeplot, "x", clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
    g.map(sns.kdeplot, "x", clip_on=False, color="w", lw=2, bw=.2)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)


    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(0, .2, label, fontweight="bold", color=color,
                ha="left", va="center", transform=ax.transAxes)


    g.map(label, "x")

    # Set the subplots to overlap
    g.fig.subplots_adjust(hspace=-.25)

    # Remove axes details that don't play will with overlap
    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)

    plt.show()
    stop = "STOP"


    #ordered_days = tips.day.value_counts().index
    #sns.distplot(data[0], kde=True, rug=False)
    #sns.distplot(data[1], kde=True, rug=False)
    #plt.show()
    #sns.violinplot(data=[data[0],data[1]],split=True, inner="stick", palette="Set3")
    #sns.violinplot(data=, split=True, inner="stick", palette="Set3")
    #plt.show()
    #g = sns.FacetGrid(data,size=1.7, aspect=1)
    #g.map(sns.distplot, "confidence", hist=False, rug=True)
    #sns.lmplot(x="x", y="y", col="dataset", hue="dataset", data=data,
    #           col_wrap=2, ci=None, palette="muted", size=2,
    #           scatter_kws={"s": 50, "alpha": 1})



