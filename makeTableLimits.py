#!/usr/bin/env python

import optparse
parser = optparse.OptionParser(description="Makes Limit Plots from output text from combine tool.")
parser.add_option("--bdtCut", help="Makes plots v. BDT Cut Instead of Luminosity",action="store_true",default=False)
parser.add_option("--cutOpt", help="Makes plots for cutOptimization",action="store_true",default=False)
parser.add_option("-m","--higgsMass", help="Makes plots v. Higgs Mass",action="store_true",default=False)
parser.add_option("--signalInject", help="Sets a caption saying that signal was injected with strength",type=float,default=0.0)
parser.add_option("--signalInjectMass", help="Mass For Injected Signal",type=float,default=125.0)
parser.add_option("-p","--printLimits", help="Just Print The Limits",action="store_true",default=False)
args, fakeargs = parser.parse_args()

from helpers import *
import ROOT as root
import glob
import re
import os.path
from copy import deepcopy
from array import array

from xsec import *

##############################################
# Only use Matplotlib if not in CMSSW_6*
cmsswVersion = ""
mplGood = True
if os.environ.has_key("CMSSW_VERSION"):
  cmsswVersion = os.environ["CMSSW_VERSION"]
#def ComparePlotTable(*arg):
#  #Dummy so that there are no errors
#  pass
if "CMSSW_6" in cmsswVersion:
  mplGood = False
if mplGood:
  from etc.evilMatPlotlibFunctions import *
##############################################


#######################################

#~48 Charactars Max
titleMap = {
  "AllCat":"H->#mu#mu Catagories Combination",
  "IncCat":"Non-VBF Categories Comb.",
  "VBFCat":"VBF Categories Comb.",

  "IncPresel":"Non-VBF Preselection",
  "VBFPresel":"VBF Preselection",

  "Pt0to30":"p_{T}^{#mu#mu} #in [0,30]",
  "Pt30to50":"p_{T}^{#mu#mu} #in [30,50]",
  "Pt50to125":"p_{T}^{#mu#mu} #in [50,125]",
  "Pt125to250":"p_{T}^{#mu#mu} #in [125,250]",
  "Pt250":"p_{T}^{#mu#mu}>250",

  "VBFLoose":"VBFL",
  "VBFMedium":"VBFM",
  "VBFTight":"VBFT",
  "VBFVeryTight":"VBFVT",

  "BDTCut":"H->#mu#mu BDT Combination",
  "IncBDTCut":"Non-VBF BDT ",
  "VBFBDTCut":"VBF BDT ",

  "BDTCutCat":"BDT Res. Cat. Combination",
  "IncBDTCutCat":"Non-VBF BDT Resolution Categories",
  "VBFBDTCutCat":"VBF BDT Resolution Categories",

  "PreselCat":"Res. Cat. Preselection Combination",
  "IncPreselCat":"Non-VBF",
  "VBFPreselCat":"VBF Cat. Resolution Preselection",

  "IncBDTCutBB":"Non-VBF BDT BB",
  "IncBDTCutBO":"Non-VBF BDT BO",
  "IncBDTCutBE":"Non-VBF BDT BE",
  "IncBDTCutOO":"Non-VBF BDT OO",
  "IncBDTCutOE":"Non-VBF BDT OE",
  "IncBDTCutEE":"Non-VBF BDT EE",
  "IncBDTCutNotBB":"Non-VBF BDT !BB",
  "VBFBDTCutBB":"VBF BDT BB",
  "VBFBDTCutNotBB":"VBF BDT !BB",
  "IncPreselBB":"Non-VBF Preselection BB",
  "IncPreselBO":"Non-VBF Preselection BO",
  "IncPreselBE":"Non-VBF Preselection BE",
  "IncPreselOO":"Non-VBF Preselection OO",
  "IncPreselOE":"Non-VBF Preselection OE",
  "IncPreselEE":"Non-VBF Preselection EE",
  "IncPreselNotBB":"Non-VBF Preselection !BB",
  "VBFPreselBB":"VBF Preselection BB",
  "VBFPreselNotBB":"VBF Preselection !BB",

  "IncPtCut":"Non-VBF",
  "VBFmDiJetCut":"VBF Cut-Based",
  "VBFdeltaEtaJetCut":"VBF Cut-Based",

  "IncPreselPtG10BB":"Non-VBF BB",
  "IncPreselPtG10BO":"Non-VBF BO",
  "IncPreselPtG10BE":"Non-VBF BE",
  "IncPreselPtG10OO":"Non-VBF OO",
  "IncPreselPtG10OE":"Non-VBF OE",
  "IncPreselPtG10EE":"Non-VBF EE",
  "IncPreselPtG10":"Non-VBF",
  "BDTCutCatVBFBDTOnly": "VBF & Non-VBF Combination",

  "Jets01PassPtG10BB": "Non-VBF Preselection, Tight BB",
  "Jets01PassPtG10BO": "Non-VBF Preselection, Tight BO",
  "Jets01PassPtG10BE": "Non-VBF Preselection, Tight BE",
  "Jets01PassPtG10OO": "Non-VBF Preselection, Tight OO",
  "Jets01PassPtG10OE": "Non-VBF Preselection, Tight OE",
  "Jets01PassPtG10EE": "Non-VBF Preselection, Tight EE",
  "Jets01PassCatAll" : "Non-VBF Preselection, Tight",
                                      
  "Jets01FailPtG10BB": "Non-VBF Preselection, Loose BB",
  "Jets01FailPtG10BO": "Non-VBF Preselection, Loose BO",
  "Jets01FailPtG10BE": "Non-VBF Preselection, Loose BE",
  "Jets01FailPtG10OO": "Non-VBF Preselection, Loose OO",
  "Jets01FailPtG10OE": "Non-VBF Preselection, Loose OE",
  "Jets01FailPtG10EE": "Non-VBF Preselection, Loose EE",
  "Jets01FailCatAll" : "Non-VBF Preselection, Loose",
                                      
  "Jets01SplitCatAll": "Non-VBF Preselection",


  "Jet2CutsVBFPass":"VBF Preselection, VBF Tight",
  "Jet2CutsGFPass":"VBF Preselection, GF Tight",
  "Jet2CutsFailVBFGF":"VBF Preselection, Loose",

  "Jet2SplitCutsGFSplit" : "VBF Preselection",
  "CombSplitAll" : "Combination",

}

comparisonMap = {
  "AllCat":"All Cat. Comb.",
  "IncCat":"!VBF Cat. Comb.",
  "VBFCat":"VBF Cat. Comb.",

  "Presel":"Presel. Comb.",
  "IncPresel":"!VBF Presel.",
  "VBFPresel":"VBF Presel.",

  "Pt0to30":"$p_{T}^{\mu\mu} \in [0,30]$",
  "Pt30to50":"$p_{T}^{\mu\mu} \in [30,50]$",
  "Pt50to125":"$p_{T}^{\mu\mu} \in [50,125]$",
  "Pt125to250":"$p_{T}^{\mu\mu} \in [125,250]$",
  "Pt250":"$p_{T}^{\mu\mu}>250$",

  "VBFLoose":"VBFL",
  "VBFMedium":"VBFM",
  "VBFTight":"VBFT",
  "VBFVeryTight":"VBFVT",

  "BDTCut":"BDT Comb.",
  "IncBDTCut":"!VBF BDT",
  "VBFBDTCut":"VBF BDT",

  "BDTCutCat":"BDT Res. Comb.",
  "IncBDTCutCat":"!VBF BDT Res.",
  "VBFBDTCutCat":"VBF BDT Res.",

  "BDTCutCatIncOnly":"BDT Comb. Inc Res.",

  #"BDTCutCat":"Combination",
  #"IncBDTCutCat":"Non-VBF",
  #"VBFBDTCutCat":"VBF",

  "PreselCat":"Presel. Res. Comb.",
  "IncPreselCat":"!VBF Res. Presel.",
  "VBFPreselCat":"VBF Res. Presel.",

  "IncBDTCutBB":"!VBF BDT BB",
  "IncBDTCutBO":"!VBF BDT BO",
  "IncBDTCutBE":"!VBF BDT BE",
  "IncBDTCutOO":"!VBF BDT OO",
  "IncBDTCutOE":"!VBF BDT OE",
  "IncBDTCutEE":"!VBF BDT EE",
  "IncBDTCutNotBB":"!VBF BDT !BB",
  "VBFBDTCutBB":"VBF BDT BB",
  "VBFBDTCutNotBB":"VBF BDT !BB",
  "IncPreselBB":"!VBF Presel. BB",
  "IncPreselBO":"!VBF Presel. BO",
  "IncPreselBE":"!VBF Presel. BE",
  "IncPreselOO":"!VBF Presel. OO",
  "IncPreselOE":"!VBF Presel. OE",
  "IncPreselEE":"!VBF Presel. EE",
  "IncPreselNotBB":"!VBF Presel. !BB",
  "VBFPreselBB":"VBF Presel. BB",
  "VBFPreselNotBB":"VBF Presel. !BB",

  "BDTCutCatVBFBDTOnly":'Comb. VBFBDT IncPreRes',
}

#######################################

def getData(fileString,matchString=r"_([-\d.]+)\.txt\.out",dontMatchStrings=[],doSort=True):
  def sortfun(s):
    match = re.search(matchString,s)
    result = 1e12
    if match:
      result = float(match.group(1))
    return result

  result = []
  fNames =  glob.glob(fileString)
  if doSort:
    fNames.sort(key=sortfun)
  #print fileString
  #print fNames
  for fname in fNames: 
    dontMatch = False
    for dont in dontMatchStrings:
      if re.search(dont,fname):
        dontMatch = True
    if dontMatch:
        continue
    tmpF = open(fname)
    match = re.search(matchString,fname)
    obs = -10.0
    median = -10.0
    low2sig = -10.0
    low1sig = -10.0
    high1sig = -10.0
    high2sig = -10.0
    xNum = -10.0
    if match:
      xNum = match.group(1)
    for line in tmpF:
      obsMatch = re.search(r"Observed[\s]Limit:[^.\d]*< ([.\deE]+)",line)
      low2sigMatch = re.search(r"Expected.*2\.5.:[^.\d]*< ([.\deE]+)",line)
      low1sigMatch = re.search(r"Expected.*16.0[^.\d]*< ([.\deE]+)",line)
      medianMatch = re.search(r"Expected.*50\.0.*< ([.\deE]+)",line)
      high1sigMatch = re.search(r"Expected.*84.0.*< ([.\deE]+)",line)
      high2sigMatch = re.search(r"Expected.*97.5.*< ([.\deE]+)",line)
      if obsMatch:
        obs = obsMatch.group(1)
      if low2sigMatch:
        low2sig = low2sigMatch.group(1)
      if low1sigMatch:
        low1sig = low1sigMatch.group(1)
      if medianMatch:
        median = medianMatch.group(1)
      if high1sigMatch:
        high1sig = high1sigMatch.group(1)
      if high2sigMatch:
        high2sig = high2sigMatch.group(1)
    thisPoint = [xNum,obs,low2sig,low1sig,median,high1sig,high2sig]
    if thisPoint.count("-10.0")>0:
        continue
    if thisPoint.count(-10.0)>0:
        continue
    #print thisPoint
    result.append(thisPoint)
  return result

class RelativePlot:
  def __init__(self,dataPoints, canvas, legend, caption, ylabel="Expected 95% CL Limit #sigma/#sigma_{SM}", xlabel="Integrated Luminosity [fb^{-1}]",caption2="",caption3="",ylimits=[],xlimits=[],vertLines=[],showObs=False,energyStr="8TeV"):
    expGraph = root.TGraph()
    expGraph.SetLineStyle(2)
    expGraph.SetMarkerStyle(20)
    expGraph.SetMarkerSize(0.9)
    oneSigGraph = root.TGraphAsymmErrors()
    oneSigGraph.SetFillColor(root.kGreen)
    oneSigGraph.SetLineStyle(0)
    twoSigGraph = root.TGraphAsymmErrors()
    twoSigGraph.SetFillColor(root.kYellow)
    twoSigGraph.SetLineStyle(0)
    oneGraph = root.TGraph()
    oneGraph.SetLineColor(root.kRed)
    oneGraph.SetLineStyle(3)
    obsGraph = root.TGraph()
    obsGraph.SetLineColor(1)
    obsGraph.SetLineStyle(1)
    obsGraph.SetLineWidth(3)
    obsGraph.SetMarkerStyle(20)
    obsGraph.SetMarkerSize(1.1)
    obsGraph.SetMarkerColor(1)
    self.expGraph = expGraph
    self.oneSigGraph = oneSigGraph
    self.twoSigGraph = twoSigGraph
    self.oneGraph = oneGraph
    self.obsGraph = obsGraph
    iPoint = 0
    ymax = 1e-20
    ymin = 1e20
    for point in dataPoints:
      xNum = float(point[0])
      if len(xlimits)==2:
        if xNum<xlimits[0]:
            continue
        if xNum>xlimits[1]:
            continue
      obs = float(point[1])
      median = float(point[4])
      low2sig = median - float(point[2])
      low1sig = median - float(point[3])
      high1sig = float(point[5]) - median
      high2sig = float(point[6]) - median
      expGraph.SetPoint(iPoint,xNum,median) 
      oneSigGraph.SetPoint(iPoint,xNum,median) 
      twoSigGraph.SetPoint(iPoint,xNum,median) 
      oneSigGraph.SetPointError(iPoint,0.0,0.0,low1sig,high1sig) 
      twoSigGraph.SetPointError(iPoint,0.0,0.0,low2sig,high2sig) 
      oneGraph.SetPoint(iPoint,xNum,1.0)
      obsGraph.SetPoint(iPoint,xNum,obs)
      iPoint += 1

      if float(point[6]) > ymax:
        ymax = float(point[6])
      if obs > ymax:
        ymax = obs

    label = root.TLatex()
    #label.SetNDC()
    label.SetTextFont(root.gStyle.GetLabelFont("X"))
    label.SetTextSize(root.gStyle.GetLabelSize("X"))
    label.SetTextColor(root.kRed)
    label.SetTextAlign(22)
    self.label=label

    twoSigGraph.Draw("a3")
    twoSigGraph.GetXaxis().SetTitle(xlabel)
    twoSigGraph.GetYaxis().SetTitle(ylabel)
    if len(ylimits)==2:
        twoSigGraph.GetYaxis().SetRangeUser(*ylimits)
    else:
        twoSigGraph.GetYaxis().SetRangeUser(0.0,ymax*1.1)
    if len(xlimits)==2:
        twoSigGraph.GetXaxis().SetRangeUser(*xlimits)
    oneSigGraph.Draw("3")
    expGraph.Draw("l")
    expGraph.Draw("p")
    #if showObs:
    #  obsGraph.Draw("l")
    #  obsGraph.Draw("p")

    tlatex = root.TLatex()
    tlatex.SetNDC()
    tlatex.SetTextFont(root.gStyle.GetLabelFont())
    #tlatex.SetTextSize(0.05)
    tlatex.SetTextSize(0.04)
    tlatex.SetTextAlign(12)
    tlatex.DrawLatex(gStyle.GetPadLeftMargin(),0.96,PRELIMINARYSTRING)
    tlatex.DrawLatex(0.02+gStyle.GetPadLeftMargin(),0.88,caption2)
    tlatex.DrawLatex(0.02+gStyle.GetPadLeftMargin(),0.82,caption3)

    tlatex.SetTextAlign(32)
    tlatex.DrawLatex(1.0-gStyle.GetPadRightMargin(),0.96,caption)

    self.vertLine = root.TLine()
    self.vertLine.SetLineColor(root.kRed)
    self.vertLine.SetLineWidth(3)
    self.arrows = []
    for xPos in vertLines:
      self.vertLine.DrawLine(xPos,ylimits[0],xPos,ylimits[1])
      xAxis = twoSigGraph.GetXaxis()
      arrowLength = (xAxis.GetXmax() - xAxis.GetXmin())/10.
      arrowY = (ylimits[1]-ylimits[0])*0.8
      arrowHeadSize = 0.025
      arrow = root.TArrow(xPos,arrowY,xPos+arrowLength,arrowY,
                                arrowHeadSize,"|>")
      arrow.SetLineWidth(3)
      arrow.SetLineColor(root.kRed)
      arrow.SetFillColor(root.kRed)
      #arrow.SetAngle(40)
      arrow.Draw()
      self.arrows += [arrow]

    canvas.RedrawAxis()

class CutOptPlots:
  def __init__(self,globName):
    self.goodDrawn=False
    self.histList = []
    self.graphList = []
    self.globName = globName
    self.canvas = root.TCanvas("CutOptCanvas")
    self.tlatex = root.TLatex()
    self.tlatex.SetNDC()
    self.tlatex.SetTextFont(root.gStyle.GetLabelFont())
    self.tlatex.SetTextSize(0.04)
    #root.gStyle.SetPalette(53)
    #root.gStyle.SetPaintTextFormat(".2f")
    root.gStyle.SetPaintTextFormat(".1f")
    files = glob.glob(globName)
    self.energyStr = ""
    self.data = {}
    for f in sorted(files):
      data =  getData(f)
      if len(data)==0:
        continue
      data =  data[0]
      data = [float(x) for x in data]
      metamatch = re.search(r"_([0-9P]+TeV)_",f)
      if metamatch:
        self.energyStr = metamatch.group(1)
        #print("Energy Str "+self.energyStr)
      else:
        print("Error: couldn't match energy string: "+f)
      f = re.sub(".*/","",f)
      f = re.sub("_8TeV.*","",f)
      f = re.sub("_7TeV.*","",f)
      f = re.sub("_7P8TeV.*","",f)
      match = re.match(r"([a-zA-Z0-9]+)_.*",f)
      assert(match)
      testName = match.group(1)
      match = re.findall(r"_([a-zA-Z0-9]+[GLS])([0-9p-]+)",f)
      assert(match)
      limit = data[4]
      #limitErr = abs(limit-data[3])
      #limitErr = max(abs(limit-data[5]),limitErr)
      #print("Relative Limit Error: {0:.1%}".format(limitErr/limit))
      tmpDict= {}
      tmpDict['limit'] = limit
      for i in match:
        val = float((i[1]).replace('p','.'))
        tmpDict[i[0]] = val
      if not self.data.has_key(testName):
        self.data[testName] = []
      self.data[testName] += [tmpDict]
    for c in self.data:
      d = self.data[c]
      d.sort(key=lambda x: x['limit'])
    if self.energyStr == "7P8TeV":
      self.energyStrWrite = "#sqrt{s} = 7 & 8 TeV"
    else:
      self.energyStrWrite = "#sqrt{s} = "+re.sub("TeV"," TeV",self.energyStr)

  def printBest(self,N):
    for c in self.data:
      print("The Best {1} For Test: {0}".format(c,N))
      for i in range(min(len(self.data[c]),N)):
        d = self.data[c][i]
        printStr = "  {limit:.2f}"
        for key in d:
          if key == 'limit':
            continue
          printStr += " "+key +' {'+key+':.1f}'
        print(printStr.format(**d))

  def plot1D(self,dataName,xName,holdConstDict,rootHistParamList):
    self.goodDrawn = False
    try:
      yMax = -1e6
      yMin = 1e6
      self.canvas.cd()
      graph = root.TGraph()
      graph.SetMarkerColor(1)
      #graph.SetMarkerSize(2*graph.GetMarkerSize())
      graph.SetLineColor(1)
      graph.SetLineWidth(2)
      data = self.data[dataName]
      iPoint = 0
      data.sort(key=lambda x: x[xName])
      for d in data:
        doContinue = False
        for sliceVar in holdConstDict:
          if not d.has_key(sliceVar):
            break
          if d[sliceVar] != holdConstDict[sliceVar]:
            doContinue = True
            break
        if doContinue:
          break
        x = d[xName]
        limit = d['limit']
        yMax = max(limit,yMax)
        yMin = min(limit,yMin)
        #print("{0}: {1:4.0f} limit: {2:4.1f}".format(xName,x,limit))
        graph.SetPoint(iPoint,x,limit)
        iPoint += 1
      xTitle = xName
      yTitle = "Median Expected Limit on #sigma/#sigma_{SM}"
      if xTitle[-1] == 'G':
          xTitle = xTitle[:-1]+" > X"
      elif xTitle[-1] == 'L':
          xTitle = xTitle[:-1]+" < X"
      else:
          raise
      graph.Draw('AC')
      xMin = graph.GetXaxis().GetXmin()
      xMax = graph.GetXaxis().GetXmax()
      padding = yMax-yMin
      yMin -= padding
      yMax += padding
      yMin = math.floor(yMin)
      yMax = math.ceil(yMax)
      hist = root.TH2F(dataName+"dummy","",1,xMin,xMax,1,yMin,yMax)
      setHistTitles(graph,xTitle,yTitle)
      setHistTitles(hist,xTitle,yTitle)
      hist.Draw()
      graph.Draw('C')
      #graph.Draw('P')
      self.graphList += [graph]
      self.histList += [hist]
      self.tlatex.SetTextAlign(12)
      self.tlatex.DrawLatex(gStyle.GetPadLeftMargin(),0.96,PRELIMINARYSTRING)
      self.tlatex.SetTextAlign(13)
      self.tlatex.DrawLatex(gStyle.GetPadLeftMargin()+0.03,1.0-gStyle.GetPadTopMargin()-0.02,self.energyStrWrite)
      self.tlatex.DrawLatex(gStyle.GetPadLeftMargin()+0.03,1.0-gStyle.GetPadTopMargin()-0.06,"L = {0:.1f} fb^{{-1}}".format(float(lumiDict[self.energyStr])))
      self.goodDrawn = True
    except LookupError as e:
      print("Warning: could not draw {0}, because key not found".format(e))

  def plot2D(self,dataName,xName,yName,holdConstDict,rootHistParamList):
    self.goodDrawn = False
    try:
      self.canvas.cd()
      hist = root.TH2F(*rootHistParamList)
      #hist.SetMarkerColor(0)
      #hist.SetMarkerSize(2*hist.GetMarkerSize())
      data = self.data[dataName]
      #print data
      for d in data:
        doContinue = False
        for sliceVar in holdConstDict:
          if not d.has_key(sliceVar):
            break
          if d[sliceVar] != holdConstDict[sliceVar]:
            doContinue = True
            break
        if doContinue:
          break
        x = d[xName]+0.00001
        y = d[yName]+0.00001
        limit = d['limit']
        ix = hist.GetXaxis().FindBin(x)
        iy = hist.GetYaxis().FindBin(y)
        hist.SetBinContent(ix,iy,limit)
        #hist.Fill(x,y)
        #print x,y,limit, d['ptMissL']
      xTitle = xName
      yTitle = yName
      if xTitle[-1] == 'G':
          xTitle = xTitle[:-1]+" > X"
      elif xTitle[-1] == 'L':
          xTitle = xTitle[:-1]+" < X"
      else:
          raise
      if yTitle[-1] == 'G':
          yTitle = yTitle[:-1]+" > Y"
      elif yTitle[-1] == 'L':
          yTitle = yTitle[:-1]+" < Y"
      else:
          raise
      setHistTitles(hist,xTitle,yTitle)
      hist.Draw('coltext')
      self.histList += [hist]
      self.tlatex.SetTextAlign(12)
      self.tlatex.DrawLatex(gStyle.GetPadLeftMargin(),0.96,PRELIMINARYSTRING)
      self.tlatex.DrawLatex(gStyle.GetPadLeftMargin(),
            gStyle.GetPadBottomMargin()*0.3,
            self.energyStrWrite+", "+"L = {0:.1f} fb^{{-1}}".format(float(lumiDict[self.energyStr]))
            )
      self.goodDrawn = True
    except LookupError as e:
      print("Warning: could not draw {0}, because key not found".format(e))

  def annotatePlot(self,text):
    if self.goodDrawn:
      optPlots.tlatex.SetTextAlign(32)
      optPlots.tlatex.DrawLatex(1.0-gStyle.GetPadRightMargin(),0.96,text)
  def save(self,fn):
    if self.goodDrawn:
      saveAs(self.canvas,fn)

if __name__ == "__main__":

  dirName = "statsInput/"
  
  outDir = "statsOutput/"
  
  root.gErrorIgnoreLevel = root.kWarning
  root.gROOT.SetBatch(True)
  setStyle()

  
  fnToGlob = dirName+"CombSplitAll_7P8TeV_*.txt.out"
  allfiles = glob.glob(fnToGlob)

  energyStr = "7 & 8 TeV"
  for fn in allfiles:
    #print fn
    data = getData(fn)[0]
    #print data
    data = [float(x) for x in data]

    mass = data[0]
    expLim = data[4]
    obsLim = data[1]
    OneSigmaPlus = data[5]
    OneSigmaMinus = data[3]
    TwoSigmaPlus = data[6]
    TwoSigmaMinus = data[2]
    
    print "%s & %.1f & XXX & ${}^{+%.1f}$ ${}_{-%.1f}$ & ${}^{+%.1f}$ ${}_{-%.1f}$ \\\\" %(mass,
                                                                                           expLim,
                                                                                           OneSigmaPlus-expLim,
                                                                                           expLim-OneSigmaMinus,
                                                                                           TwoSigmaPlus-expLim,
                                                                                           expLim-TwoSigmaMinus)
    print "\\hline"
    
