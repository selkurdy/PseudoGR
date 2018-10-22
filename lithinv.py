"""
Rotate Acoustic Impedence and Shear Impedence to generate Psuedo Gamma Ray.

python lithinv.py ai.segy si.segy
python lithinv.py ai.segy si.segy --hideplots
"""
import os.path
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import segyio
from shutil import copyfile
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.preprocessing import MinMaxScaler


def lineslope(ai,si):
    """Compute slope of line between ai and si."""
    cf = np.polyfit(ai, si, 1)
    return cf[0]


def lith(ai, si, a, indeg=False):
    """Rotation of data."""
    if indeg:
        a = np.deg2rad(a)
    lithinv = ai * np.cos(a) - si * np.sin(a)
    return lithinv


def minmaxscale(x, minx=None, maxx=None):
    """Scale resulting log to min max."""
    if not minx:
        minx = x.min()
    if not maxx:
        maxx = x.max()
    x_std = (x - x.min()) / (x.max() - x.min())
    x_scaled = x_std * (maxx - minx) + minx
    return x_scaled


def getcommandline():
    """Main."""
    parser = argparse.ArgumentParser(description='Compute Gamma Ray Logs from Acoustic impedence and Shear impedence')
    parser.add_argument('aisegy', help='AI segy')
    parser.add_argument('sisegy',help='SI segy')
    parser.add_argument('--aiminmaxscaler',action='store_true',default=False,
        help='apply min max scaler to scale AI & SI traces.default do not apply')
    parser.add_argument('--aiscalemm',nargs=2,type=float,default=(1000,2000),
        help='Min Max values to scale AI & SI traces. default= 1000 2000')

    parser.add_argument('--liminmaxscaler',action='store_true',default=False,
        help='apply min max scaler to computed Psuedo GR. default do not apply')
    parser.add_argument('--liscalemm',nargs=2,type=float,default=(0,150),
        help='Min Max values to scale output computed Psuedo GR trace. default 0 150')

    parser.add_argument('--xhdr',type=int,default=73,help='xcoord header.default=73')
    parser.add_argument('--yhdr',type=int,default=77,help='ycoord header. default=77')
    parser.add_argument('--xyscalerhdr',type=int,default=71,help='hdr of xy scaler to divide by.default=71')
    parser.add_argument('--todegrees',action='store_true',default=False,
        help='convert angle to degrees. default= randians')
    parser.add_argument('--plottrace',type=int,default=50000,
        help='plot increment. default=50000')
    parser.add_argument('--outdir',help='output directory,default= same dir as input')
    parser.add_argument('--hideplots',action='store_true',default=False,
                        help='Only save to pdf. default =show and save')

    result = parser.parse_args()
    return result


def main():
    """main."""
    cmdl = getcommandline()
    aidirsplit,aifextsplit = os.path.split(cmdl.aisegy)
    aifname, aifextn = os.path.splitext(aifextsplit)

    sidirsplit, sifextsplit = os.path.split(cmdl.sisegy)
    sifname, sifextn = os.path.splitext(sifextsplit)

    outfn = aifname + sifname
    if cmdl.outdir:
        outfname = os.path.join(cmdl.outdir, outfn) + "_li.sgy"
        lithpdf = os.path.join(cmdl.outdir, outfn) + "_li.pdf"
        # tracefname = os.path.join(cmdl.outdir, outfn) + "_litrc.csv"
    else:
        outfname = os.path.join(aidirsplit, outfn) + "_li.sgy"
        lithpdf = os.path.join(aidirsplit, outfn) + "_li.pdf"
        # tracefname = os.path.join(aidirsplit, outfn) + "_litrc.csv"
    print('Copying file, please wait ........')
    start_copy = datetime.now()
    copyfile(cmdl.aisegy, outfname)
    end_copy = datetime.now()
    print('Duration of copying: {}'.format(end_copy - start_copy))

    start_process = datetime.now()
    xclst = list()
    yclst = list()
    alst = list()
    if cmdl.aiminmaxscaler:
        aisclmm = MinMaxScaler((cmdl.aiscalemm[0],cmdl.aiscalemm[1]))

    if cmdl.liminmaxscaler:
        lisclmm = MinMaxScaler((cmdl.liscalemm[0],cmdl.liscalemm[1]))

    # trcols = ['TRNUM', 'X','Y', 'AI','SI','LI']
    # ailst = list()
    # silst = list()
    # lilst = list()
    with segyio.open(cmdl.aisegy, "r") as aisrc, segyio.open(cmdl.sisegy, "r") as sisrc:
        with segyio.open(outfname,"r+") as lisrc:
            with PdfPages(lithpdf) as pdf:
                trnum = 0
                xysch = np.fabs(aisrc.header[trnum][cmdl.xyscalerhdr])
                if xysch == 0:
                    xysc = 1.0
                else:
                    xysc = xysch
                for aitrace,sitrace,litrace in zip(aisrc.trace,sisrc.trace,lisrc.trace):
                    xclst.append(aisrc.header[trnum][cmdl.xhdr] / xysc)
                    yclst.append(aisrc.header[trnum][cmdl.yhdr] / xysc)
                    if cmdl.aiminmaxscaler:
                        aitrace = aisclmm.fit_transform(aitrace.reshape(-1, 1))
                        sitrace = aisclmm.fit_transform(sitrace.reshape(-1, 1))
                        aitrace = aitrace.reshape(-1)
                        sitrace = sitrace.reshape(-1)
                    if trnum % 100 == 0:
                        print('Trace #: {}'.format(trnum))
                    liangle = np.pi / 2.0 - lineslope(aitrace, sitrace)
                    alst.append(liangle)
                    if np.all(aitrace == 0) and np.all(sitrace == 0):
                        # just copy the ai trace into the resulting lith file
                        lisrc.trace[trnum] = aitrace
                    else:
                        # litr = minmaxscale(lith(aitrace,sitrace,liangle),cmdl.minmaxscaler[0],cmdl.minmaxscaler[1])
                        litr = lith(aitrace,sitrace, liangle)
                        if cmdl.liminmaxscaler:
                            litr = lisclmm.fit_transform(litr.reshape(-1, 1))
                            litr = litr.reshape(-1)

                        lisrc.trace[trnum] = litr

                        if trnum % cmdl.plottrace == 0:
                            fig,ax = plt.subplots(1,3,figsize=(6, 7))
                            ax[0].invert_yaxis()
                            ax[1].invert_yaxis()
                            ax[2].invert_yaxis()
                            # ax.plot(aitrace, range(aitrace.size), c='r', label='AI')
                            # ax.plot(sitrace, range(sitrace.size), c='g', label='SI')
                            # ax.plot(litr, range(litr.size), c='b', label='LI')
                            # ax.legend()

                            ax[0].plot(aitrace, range(aitrace.size), c='r')
                            ax[1].plot(sitrace, range(sitrace.size), c='g')
                            ax[2].plot(litr, range(litr.size), c='b')
                            ax[0].set_xlabel('AI')
                            ax[1].set_xlabel('SI')
                            ax[2].set_xlabel('LI')
                            fig.suptitle('Trace #: {} X: {},Y: {} '.format(trnum,xclst[trnum],yclst[trnum]), y=0.02)
                            # ax.set_title('Trace #: {} X: {},Y: {} '.format(trnum,xclst[trnum],yclst[trnum]))
                            # ax.set_xlabel('Acoustic/Shear/Lithology impedence')
                            # ax.set_ylabel('Samples')
                            fig.tight_layout()
                            pdf.savefig()
                            if not cmdl.hideplots:
                                plt.show()
                            plt.close()

                    trnum += 1
            print('Successfully generated %s ' % lithpdf)
    print('Successfully wrote %s ' % outfname)
    end_process = datetime.now()
    print('Duration of processing: {}'.format(end_process - start_process))
    cols = ['X','Y','Angle']
    if cmdl.outdir:
        adfname = os.path.join(cmdl.outdir,outfn) + "_ang.csv"
        adfnametxt = os.path.join(cmdl.outdir,outfn) + "_ang.txt"
    else:
        adfname = os.path.join(aidirsplit,outfn) + "_ang.csv"
        adfnametxt = os.path.join(aidirsplit,outfn) + "_ang.txt"
    if cmdl.todegrees:
        angles = np.rad2deg(np.array(alst))
        angledf = pd.DataFrame({'X':xclst,'Y':yclst,'Angle':angles})
        print('Converted to degrees')
    else:
        angledf = pd.DataFrame({'X':xclst,'Y':yclst,'Angle':alst})

    angledf = angledf[cols].copy()
    angledf.to_csv(adfname,index=False)
    angledf.to_csv(adfnametxt,index=False,sep=' ')
    print('Successfully generated {} and {}'.format(adfname,adfnametxt))


if __name__ == '__main__':
    main()
