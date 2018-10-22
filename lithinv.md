#  LITHINV  
> Given both acoustic impedance and shear impedence volumnes (segy) each trace is crossplotted and rotated to result in a pseudo gamma ray trace. A segy is generated. 

>  The pseudo gamma ray volume will obviously have the resolution of the seimic.  


##  COMMAND LINE INTERFACE

```
python lithinv.py -h
usage: lithinv.py [-h] [--aiminmaxscaler] [--aiscalemm AISCALEMM AISCALEMM]
                  [--liminmaxscaler] [--liscalemm LISCALEMM LISCALEMM]
                  [--xhdr XHDR] [--yhdr YHDR] [--xyscalerhdr XYSCALERHDR]
                  [--todegrees] [--plottrace PLOTTRACE] [--outdir OUTDIR]
                  [--hideplots]
                  aisegy sisegy

Compute Gamma Ray Logs from Acoustic impedence and Shear impedence

positional arguments:
  aisegy                AI segy
  sisegy                SI segy

optional arguments:
  -h, --help            show this help message and exit
  --aiminmaxscaler      apply min max scaler to scale AI & SI traces.default
                        do not apply
  --aiscalemm AISCALEMM AISCALEMM
                        Min Max values to scale AI & SI traces. default= 1000
                        2000
  --liminmaxscaler      apply min max scaler to computed Psuedo GR. default do
                        not apply
  --liscalemm LISCALEMM LISCALEMM
                        Min Max values to scale output computed Psuedo GR
                        trace. default 0 150
  --xhdr XHDR           xcoord header.default=73
  --yhdr YHDR           ycoord header. default=77
  --xyscalerhdr XYSCALERHDR
                        hdr of xy scaler to divide by.default=71
  --todegrees           convert angle to degrees. default= randians
  --plottrace PLOTTRACE
                        plot increment. default=50000
  --outdir OUTDIR       output directory,default= same dir as input
  --hideplots           Only save to pdf. default =show and save

```   

##  CONCEPT  


>  The program can work on either the acoustic/shear impedance volumes generated from inversion, or on relative acoustic/shear impedance generated from post stack data. The assumption of course, is that the user has a PS volume that has been processed to PP time.  

> As a matter of fact, you can run it on the depth volumes, i.e. run the post stack relative acoutic impedance or colored inversion on both the PP and PS volumes.  

>  The program has been tested on several areas with good results, i.e. LI traces matchin quite nicely with the existing gamma ray at well locations, with the obvious caveat that the traces are of much lower resolution than those of the well gamma ray logs.  

>  There is an option to scale the resulting pseudo gamma ray traces to the raanges seen by normal gamma ray logs. The scaling limits are user defined.  
