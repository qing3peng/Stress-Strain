#!/usr/bin/python   

# --------------- readme plot_tensile_stress_strain.py -----------------------------------
# This python3 script plot_tensile_stress_strain.py is a post-processing code 
# for tensile simulation. The main tasks are following: 
#
#    1. plot the stress-strain curve 
#    2. linear fit to obtain the Young's modulus 
#    3. get the ultimate tensile strength
#    4. integration to obtain the tensile toughness 
#    5. determin the failure strain
# 
# For ease of your understanding, I tried to add as more comments as I can
# Please adopt it for your system/projets
# Qing Peng on 2021.07.12; qpeng.org@gmail.com; http://qpeng.org 
# The update of this script on github: https://github.com/qing3peng/Stress-Strain
# ------------------------------------------------------------------------------------------

# ------------------importing the needed libraries------------------------------------------
import os,sys                                       #import OS and SYS module 
import numpy as np                                  #import numpy library
import matplotlib.pyplot as plt                     #import matplot library (pyplot module )
from scipy import integrate as intg                 #import scipy library (integrate module)
import argparse                                     #import argparse for argment processing

def usage(msg=''):
    ss=''' Usage example: python ./plot_tensile_stress_strain.py result_CNT_tensile.dat --title 'Defective CNT' --xlim 0 0.2 --ylim 0 60 --Yn 50
    '''
    ss += msg
    print(ss)
    return ss
#------------------ parse arguments and options --------------------------------------------
parser = argparse.ArgumentParser() # please change the default value for ease of your work
parser.add_argument('file', help='inputfile',default='')
parser.add_argument('-t',help='fitting-type',type=int,default=2)
parser.add_argument('--file2', help='inputfile2',default='')
parser.add_argument('--title', help='title of the figure',default='Tensile')
parser.add_argument('--j1', help='x colomn',type=int,default=2)
parser.add_argument('--j2', help='y colomn',type=int,default=3)
parser.add_argument('--Yn', help='number of points to be used for Young fitting',type=int,default=10)
parser.add_argument('--xlim', help='x limit',nargs=2,type=float,default=[0.0,0.0])
parser.add_argument('--ylim', help='y limit',nargs=2,type=float,default=[0.0,0.0])
parser.add_argument('--kk', help='MaxNLocator',nargs=2,type=int,default=[0,0])
parser.add_argument('--label', help='label',default='MD:fitting')
parser.add_argument('--lw', help='linewidth',type=float,default=2.0)
parser.add_argument('--lw2', help='linewidth',type=float,default=1.0)
parser.add_argument('--alpha', help='transparency',type=float,default=0.8)
parser.add_argument('--xlabel', help='axis label',default='Strain:Stress (GPa)')
parser.add_argument('--tx', help='text position',nargs=2,type=int,default=[0.005,0.7])
parser.add_argument('--xfsize', help='axis fontsize',type=int,default=14)
parser.add_argument('--txtfsize', help='text size',type=int,default=10)
parser.add_argument('--legfsize', help='legend text size',type=int,default=10)
parser.add_argument('--loc', help='legend location',default='best')
parser.add_argument('--dpi', help='resolution',type=float,default=300.0)
args = parser.parse_args()
ss_args=' '.join(sys.argv)
fw=open('readme.plotting','w');fw.write(ss_args);fw.close()
Nargv = len(sys.argv)
prog=os.path.basename(sys.argv[0])

print("Welcome to %s"%prog)
print()
usage()
#------------------ cutomize input -------------------------------
# Customized input with default and accepted values
def myinput(prompt, default, accepted):
    while True:
        res = input(prompt + " [default=%s]: " % (default))
        if res == '': res = default
        if res in accepted:
            break
        else:
            print("accepted values:", accepted)
    return res

if Nargv == 1:
    fname = input("Filename containing stress vs strain [stress_strain.dat]: ")
    if fname == '': fname = 'stress_strain.dat'
else:
    fname = sys.argv[1]

try:
    f = open(fname, 'rt')
except IOError:
    sys.stderr.write("Error opening or reading file %s\n" % (fname))
    sys.exit(1)

#------------------ linear fit y=kx for Young's modulus ---------------------
def Young_fit(x,y):
    # Our model is y = a * x, so things are quite simple, in this case...
    # x needs to be a column vector instead of a 1D vector for this, however.
    x = x[:,np.newaxis]
    k, _, _, _ = np.linalg.lstsq(x, y,rcond=None)
    print('fiting to y=k*x : slope k =',k)
    return k

#------------------  importing data (using j1,j2 to plot different data/column  -------------------
Data=np.loadtxt(fname)                              #import the data in the text with specified path
strain=Data[:,args.j1-1]                            #define the strain values # the second column
stress=Data[:,args.j2-1]                            #define the stress values # the third column

n=int(args.Yn)                                      #Number of points to fit 
strainfit=strain[:n]                                #define the strain values fit
stressfit=stress[:n]                                #define the stress values fit
x1 =np.linspace(0,0.1,100)                          #define an array with 100 points from 0 to 0.1
if args.file2 != '':
    M=np.loadtxt(args.file2) 
    X2,Y2=M[:,args.j1-1],M[:,args.j2-1]
    x2,y2=X2[:n],Y2[:n]

if args.t==1:                                       # fitting type 1: using polyfit 
    fit = np.polyfit(strainfit,stressfit,1)         #fit the specified values (linear fit)
    yfit =np.polyval(fit,x1)
    if args.file2 != '':
        fit2 = np.polyfit(x2,y2,1)                  #fit the specified values (linear fit)
        yfit2 =np.polyval(fit2,x2)
elif args.t==2:                                     # fitting type 2: using home-made Young_fit function
    k = Young_fit(strainfit,stressfit)
    yfit=k*x1                                       #define an array with 100 points from 0 to 0.1
    if args.file2 != '':
        k2 = Young_fit(x2,y2)
        yfit2=k2*x1                                 #define an array with 100 points from 0 to 0.1

#-----------------plot and  texting the results ----------------------------------
plt.figure(num=1,dpi=args.dpi)                      #specifiy the figure number and the resolution 
plt.title(args.title)                     #figure title: for tensile test

if args.label: lab = args.label.split(':')          # curve labels, string with ":" seperation
if args.xlabel: xlab = args.xlabel.split(':')       # axis labels, strings with ":" seperation
    
l1,=plt.plot(strain,stress,'r-',label=lab[0], linewidth=args.lw)  #plot the stress-strain curve
# add the fitting curve
if args.file2 != '':
    if args.t>0: l2,=plt.plot(x1,yfit,label=lab[1],linewidth=args.lw2,color="r",linestyle="--",alpha=args.alpha) #Plot the fit data
else:
    if args.t>0: l2,=plt.plot(x1,yfit,label=lab[1],linewidth=args.lw2,color="b",linestyle="--",alpha=args.alpha) #Plot the fit data

# add second stress-strain curve for comprison (you can do more as you can)
if args.file2 != '':
    l21,=plt.plot(X2,Y2,'b-',label=lab[2], linewidth=2)    #plot the stress-strain curve
    if args.t>0: l22,=plt.plot(x1,yfit2,'b:',label=lab[3], linewidth=args.lw2,alpha=args.alpha)    #plot the stress-strain curve

plt.xlabel(xlab[0], fontsize=args.xfsize)           #x-axis lable and style
plt.ylabel(xlab[1], fontsize=args.xfsize)           #y-axis lable and style

if args.xlim[1] != args.xlim[0]: plt.xlim(args.xlim)               # adjust xlim
if args.ylim[1] != args.ylim[0]: plt.ylim(args.ylim)               # adjust ylim

#-----------------  texting the results ----------------------------------
axes = plt.gca()
y_min, y_max = axes.get_ylim()

ss = ''
if args.t >0:
    Young=k
    jc=np.argmax(stress)                                #Find the maximum stress value
    Strength=stress[jc]
    Fstrain=strain[jc]                                  #Find the maximum strain value
    half_strength = 0.5*Strength
    res=np.where(stress[jc:] > half_strength)
    jd=len(res)+jc
    Toughness=intg.trapz(stress[:jd],strain[:jd])       #Estimate the integral of the data
    ss = "   Data analysis \n"
    ss +="Young's  modulus: %.1f GPa \n"%Young
    ss +="Material strength:  %.1f GPa \n"%Strength
    ss +="Material toughness: %.3f \n"%Toughness
    ss +="Fracture strain:    %.3f \n"%Fstrain
    
    if args.file2 != '':
        Young2=k2
        jc2=np.argmax(Y2)                               #Find the maximum stress value
        Strength2=Y2[jc2]
        Fstrain2=X2[jc2]                                #Find the maximum strain value
        half_strength2=0.5*Strength2
        res2=np.where(Y2[jc:] > half_strength2)
        jd2=len(res2)+jc2
        Toughness2=intg.trapz(Y2[:jd2],X2[:jd2])        #Estimate the integral of the data
    
        ss = "   Data analysis \n"
        ss +="Young's  modulus: %5.1f|%5.1f GPa \n"%(Young,Young2)
        ss +="Material strength:  %4.1f|%4.1f GPa \n"%(Strength,Strength2)
        ss +="Material toughness: %5.3f|%5.3f \n"%(Toughness,Toughness2)
        ss +="Fracture strain:    %5.3f|%5.3f \n"%(Fstrain,Fstrain2)

#add text to the figure 
tx=args.tx[0]
ty=y_max*args.tx[1]
plt.text(tx,ty, ss,color="navy",fontsize=args.txtfsize) 

plt.xticks(fontsize=args.xfsize)                    # controlling the size of xticks
plt.yticks(fontsize=args.xfsize)                    # controlling the size of yticks
plt.grid()                                          # add gird     
plt.legend(fontsize=args.legfsize,loc=args.loc)     # add legend

if args.kk[0]>0: axis.xaxis.set_major_locator(plt.MaxNLocator(args.kk[0]))  # adjust number of ticks
if args.kk[1]>0: axis.yaxis.set_major_locator(plt.MaxNLocator(args.kk[1]))  # adjust number of ticks

#-----------------   save figure and results ----------------------------------
fname += "_%d_%d"%(args.j1,args.j2)
if args.file2 != '':
    fname += "_"+args.file2.split('/')[-1]
if args.t>0:
    fname += "_%d"%(int(Young))
#plt.savefig("stress_starin_Curve.png")             #Save the figure 
plt.savefig('ss'+fname+".png")

#--- print the fitting results on the screen  and save to file  -----------------------
if args.t>0: #                                  saving fitting results
    print(ss)
    fw=open(fname+'_fitting_results.txt','w')
    fw.write(ss)
    fw.close()

#-----------------   showing the plot now ----------------------------------
plt.show()
# --------------- DONE  end of plot_tensile_stress_strain.py ----------------------------

