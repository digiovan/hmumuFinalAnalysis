#!/usr/bin/env python

from helpers import *
import ROOT as root
import cPickle
from xsec import *
from scipy.stats import norm

PRELIMINARYSTRING="CMS Internal"
root.gStyle.SetMarkerSize(0.9)

###############################################################33

limits160F = open("limitsCombSplitAll7P8TeV_110160.pkl")
limits170F = open("limitsCombSplitAll7P8TeV_110170.pkl")

pvals160F = open("pValuesCombSplitAll7P8TeV_110160.pkl")
pvals170F = open("pValuesCombSplitAll7P8TeV_110170.pkl")

limits160 = cPickle.load(limits160F)
limits170 = cPickle.load(limits170F)
pvals160 = cPickle.load(pvals160F)
pvals170 = cPickle.load(pvals170F)

obs160G = root.TGraph()
obs170G = root.TGraph()
exp160G = root.TGraph()
exp170G = root.TGraph()

for i,entry in zip(range(len(limits160)),limits160):
  obs160G.SetPoint(i,float(entry[0]),float(entry[1]))
  exp160G.SetPoint(i,float(entry[0]),float(entry[4]))
  print 
for i,entry in zip(range(len(limits170)),limits170):
  obs170G.SetPoint(i,float(entry[0]),float(entry[1]))
  exp170G.SetPoint(i,float(entry[0]),float(entry[4]))

pvals160G = root.TGraph()
pvals170G = root.TGraph()

print "#########################3\n110-160\n"
for i,entry in zip(range(len(pvals160)),pvals160):
  pvals160G.SetPoint(i,float(entry[0]),float(entry[1]))
  print entry[0],norm.isf(float(entry[1]))
print "#########################3\n110-170\n"
for i,entry in zip(range(len(pvals170)),pvals170):
  pvals170G.SetPoint(i,float(entry[0]),float(entry[1]))
  print entry[0],norm.isf(float(entry[1]))

###############################################################33

obs160G.SetLineColor(root.kBlue)
obs160G.SetMarkerColor(root.kBlue)
exp160G.SetLineColor(root.kBlue)
exp160G.SetMarkerColor(root.kBlue)

obs170G.SetLineColor(root.kRed)
obs170G.SetMarkerColor(root.kRed)
exp170G.SetLineColor(root.kRed)
exp170G.SetMarkerColor(root.kRed)

pvals160G.SetLineColor(root.kBlue)
pvals160G.SetMarkerColor(root.kBlue)
pvals170G.SetLineColor(root.kRed)
pvals170G.SetMarkerColor(root.kRed)

exp160G.SetLineStyle(2)
exp170G.SetLineStyle(2)

###############################################################33

canvas = root.TCanvas("canvas")

tlatex = root.TLatex()
tlatex.SetNDC()
tlatex.SetTextFont(root.gStyle.GetLabelFont())
tlatex.SetTextSize(0.04)

axisHist = root.TH2F("axisHist","",1,110,160,1,0,50)
setHistTitles(axisHist,"M(#mu#mu) [GeV/c^{2}]","95% CL Limit on #sigma/#sigma_{SM} (H#rightarrow#mu#mu)")
axisHist.Draw()

exp170G.Draw("L")
exp160G.Draw("L")
obs170G.Draw("LP")
obs160G.Draw("LP")

leg = root.TLegend(0.172,0.905,0.73,0.585)
leg.SetLineColor(0)
leg.SetFillColor(0)
leg.AddEntry(obs160G,"Observed M(#mu#mu) #in [110,160] GeV/c^{2}","lp")
leg.AddEntry(exp160G,"Expected M(#mu#mu) #in [110,160] GeV/c^{2}","l")
leg.AddEntry(obs170G,"Observed M(#mu#mu) #in [110,170] GeV/c^{2}","lp")
leg.AddEntry(exp170G,"Expected M(#mu#mu) #in [110,170] GeV/c^{2}","l")
leg.Draw()

tlatex.SetTextAlign(12)
tlatex.DrawLatex(gStyle.GetPadLeftMargin(),0.96,PRELIMINARYSTRING)
tlatex.SetTextAlign(32)
tlatex.DrawLatex(1.0-gStyle.GetPadRightMargin(),0.96,"H#rightarrow#mu#mu Combination 2011+2012")

saveAs(canvas,"output/limitsCompare")

##############################################

canvas.SetLogy(1)

xmin = 110
xmax = 160
ymin = 1e-4
ymax = 1.

axisHist = root.TH2F("axisHist2","",1,xmin,xmax,1,ymin,ymax)
setHistTitles(axisHist,"M(#mu#mu) [GeV/c^{2}]","p-value")
axisHist.Draw()

pvals170G.Draw("LP")
pvals160G.Draw("LP")

hLine = root.TLine()
hLine.SetLineWidth(3)
hLine.SetLineStyle(3)
hLine.SetLineColor(1)
latex = root.TLatex()
latex.SetTextFont(root.gStyle.GetLabelFont("X"))
latex.SetTextSize(root.gStyle.GetLabelSize("X"))
latex.SetTextAlign(11)
latex.SetTextColor(1)

for y,iSigma in zip([norm.sf(i) for i in range(1,7)],range(1,7)):
  if y < ymin:
    continue
  hLine.DrawLine(xmin,y,xmax,y)
  latex.DrawLatex(xmin+0.05*(xmax-xmin),y*1.05,"{0}#sigma".format(iSigma))

leg = root.TLegend(0.172,0.16,0.78,0.34)
leg.SetLineColor(0)
leg.SetFillColor(0)
leg.AddEntry(pvals160G,"M(#mu#mu) #in [110,160] GeV/c^{2}","lp")
leg.AddEntry(pvals170G,"M(#mu#mu) #in [110,170] GeV/c^{2}","lp")
leg.Draw()

tlatex.SetTextAlign(12)
tlatex.DrawLatex(gStyle.GetPadLeftMargin(),0.96,PRELIMINARYSTRING)
tlatex.SetTextAlign(32)
tlatex.DrawLatex(1.0-gStyle.GetPadRightMargin(),0.96,"H#rightarrow#mu#mu Combination 2011+2012")

saveAs(canvas,"output/pvalsCompare")

#raw_input("press enter to continue...")

