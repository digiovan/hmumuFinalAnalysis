#!/usr/bin/env python

import math
from math import sqrt
import ROOT as root
from helpers import *
import matplotlib.pyplot as mpl
import numpy
import glob
import re

from xsec import *

import makeShapePlots

channelNameMap = {
  "AllCat":"All Cat. Comb.",
  "IncCat":"Inc. Cat. Comb.",
  "VBFCat":"VBF Cat. Comb.",

  "Presel":"Presel. Comb.",
  "IncPresel":"Inc. Presel.",
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
  "IncBDTCut":"Inc. BDT",
  "VBFBDTCut":"VBF BDT",

  "BDTCutCat":"BDT Res. Comb.",
  "IncBDTCutCat":"Inc. BDT Res.",
  "VBFBDTCutCat":"VBF BDT Res.",

  "PreselCat":"Presel. Res. Comb.",
  "IncPreselCat":"Inc. Res. Presel.",
  "VBFPreselCat":"VBF Res. Presel.",

  "IncBDTCutBB":"Inc. BDT BB",
  "IncBDTCutBO":"Inc. BDT BO",
  "IncBDTCutBE":"Inc. BDT BE",
  "IncBDTCutOO":"Inc. BDT OO",
  "IncBDTCutOE":"Inc. BDT OE",
  "IncBDTCutEE":"Inc. BDT EE",
  "IncBDTCutNotBB":"Inc. BDT !BB",
  "VBFBDTCutBB":"VBF BDT BB",
  "VBFBDTCutNotBB":"VBF BDT !BB",
  "IncPreselBB":"Inc. Presel. BB",
  "IncPreselBO":"Inc. Presel. BO",
  "IncPreselBE":"Inc. Presel. BE",
  "IncPreselOO":"Inc. Presel. OO",
  "IncPreselOE":"Inc. Presel. OE",
  "IncPreselEE":"Inc. Presel. EE",
  "IncPreselNotBB":"Inc. Presel. !BB",
  "VBFPreselBB":"VBF Presel. BB",
  "VBFPreselNotBB":"VBF Presel. !BB"
}

sampleNameMap = {
  "data_obs":"Data",
  "bak":"Background",
  "sig":"Signal"
}
errNameMap = {
  "expParam":"Exponential Param.",
  "voitSig":"Voigtian $\sigma$",
  "voitmZ":"Voigtian Mass",
  "mixParam":"V/E Ratio",
  "TotalSyst":"Total Systematic",
  "Stat":"Statistical",

  "lumi":"Luminosity",
  "br_Hmm":r"BR($H\rightarrow\mu\mu$)",
  "xs_ggH":r"$\sigma(gg\rightarrow H)$",
  "xs_vbfH":r"$\sigma(gg \rightarrow H)$",
  "xs_wH":r"$\sigma(WH)$",
  "xs_zH":r"$\sigma(ZH)$",

  "ResASig":r"Muon Smearing $\sigma$",
  "ResSig":r"Muon Smearing Mixing",
}

def convertHistToCounts(dataDict,ggFileName,vbfFileName):
  ggFile = root.TFile(ggFileName)
  vbfFile = root.TFile(vbfFileName)

  outDict = {}
  for channelName in dataDict:
    tmpHist = None
    histNameToGet = channelName+"/mDiMu"
    if re.search("VBF",channelName) or re.search("vbf",channelName):
      tmpHist = vbfFile.Get(histNameToGet)
    else:
      tmpHist = ggFile.Get(histNameToGet)
    quantiles = getMedianAndQuantileInterval(tmpHist,0.159)
    tmpDict = {}
    channel = dataDict[channelName]
    lowBin = 0
    highBin = 0
    for histName in channel:
      hist = channel[histName]
      val = getIntegralAll(hist,[quantiles[0],quantiles[2]])
      tmpDict[histName] = val
    outDict[channelName] = tmpDict
  return outDict
  
def getShapeErrorsFromCounts(data):
  outDict = {}
  for channelName in data:
    tmpDict = {}
    channel = data[channelName]
    for name in channel:
      if name == "data_obs":
        tmpDict["data_obs"] = {"nom":channel[name]}
        continue
      matchUp = re.match(r"([^_]+)_(.+)Up",name)
      matchDown = re.match(r"([^_]+)_(.+)Down",name)
      if matchUp:
        histName = matchUp.group(1)
        parName = matchUp.group(2)
        if tmpDict.has_key(histName):
          if tmpDict[histName].has_key(parName):
            tmpDict[histName][parName]["Up"] = channel[name]
          else:
            tmpDict[histName][parName] = {}
            tmpDict[histName][parName]["Up"] = channel[name]
        else:
          tmpDict[histName] = {}
          tmpDict[histName][parName] = {}
          tmpDict[histName][parName]["Up"] = channel[name]
      elif matchDown:
        histName = matchDown.group(1)
        parName = matchDown.group(2)
        if tmpDict.has_key(histName):
          if tmpDict[histName].has_key(parName):
            tmpDict[histName][parName]["Down"] = channel[name]
          else:
            tmpDict[histName][parName] = {}
            tmpDict[histName][parName]["Down"] = channel[name]
        else:
          tmpDict[histName] = {}
          tmpDict[histName][parName] = {}
          tmpDict[histName][parName]["Down"] = channel[name]
      else:
        if tmpDict.has_key(name):
          tmpDict[name]["nom"] = channel[name]
        else:
          tmpDict[name] = {"nom":channel[name]}
    ##################################
    # Now Process into Error Fractions
    for histName in tmpDict:
      print histName
      nomVal = tmpDict[histName]["nom"]
      upSum2 = 0.0
      downSum2 = 0.0
      for errName in tmpDict[histName]:
        if errName == "nom":
            continue
        upVal = tmpDict[histName][errName]["Up"]
        downVal = tmpDict[histName][errName]["Down"]
        if upVal < downVal:
          tmpVal = upVal
          upVal = downVal
          downVal = tmpVal
        upErr = (upVal-nomVal)/nomVal
        downErr = (nomVal-downVal)/nomVal
        tmpDict[histName][errName]["Up"] = upErr
        tmpDict[histName][errName]["Down"] = downErr
        upSum2 += upErr**2
        downSum2 += downErr**2
      if histName == "bak":
        tmpDict[histName]["TotalSyst"] = {"Up":sqrt(upSum2),"Down":sqrt(downSum2)}
        tmpDict[histName]["Stat"] = {"Up":sqrt(nomVal)/nomVal,"Down":sqrt(nomVal)/nomVal}
      if histName == "sig":
        tmpDict[histName]["TotalSyst"] = {"Up":sqrt(upSum2),"Down":sqrt(downSum2)}

    for histName in tmpDict:
        print(histName+"  "+str(tmpDict[histName].keys()))
        
    outDict[channelName] = tmpDict
      
      
  return outDict

def writeErrorTable(data,latex,niceTitles,mustMatchList=None,cantMatchList=None,sampleMustBe=""):
  def sortfun(s):
    ll = ["BB","BE","BO","OO","OE","EE","NotBB","!BB"]
    i = 0
    for l in ll:
      match = re.match(r"(.*)("+l+r")",s)
      if match:
        result = match.group(1)+str(i)
        return result
      i += 1
    return s
  def matches(s,ll):
    for l in ll:
      if re.match(l,s):
        return True
    return False
  outString = ""
  # Get Widths
  maxChannelWidth = 0
  maxSampleWidth = 0
  maxErrWidth = 0
  channelNames = data.keys()
  channelNames.sort(key=sortfun)
  for channelName in channelNames:
     channel = data[channelName]
     if niceTitles:
        channelName = channelNameMap[channelName]
     if len(channelName) > maxChannelWidth:
        maxChannelWidth = len(channelName)
     for sampleName in channel:
       if not re.search(sampleMustBe,sampleName):
         continue
       sample = channel[sampleName]
       if niceTitles:
         sampleName = sampleNameMap[sampleName]
       if len(sampleName) > maxSampleWidth:
          maxSampleWidth = len(sampleName)
       for errName in sample:
         if mustMatchList != None:
            if not matches(errName, mustMatchList):
              continue
         if cantMatchList != None:
            if matches(errName, cantMatchList):
              continue
         if errName == "nom":
            continue
         if niceTitles:
           errName = errNameMap[errName]
         if len(errName) > maxErrWidth:
            maxErrWidth = len(errName)
  maxChannelWidth = str(maxChannelWidth+2)
  maxSampleWidth = str(maxSampleWidth+2)
  maxErrWidth = str(maxErrWidth+2)
  # Get Err Names
  errNames = []
  errNamesString = " "*int(maxChannelWidth)
  if latex:
    errNamesString += "&"
  iErrName = 0
  for channelName in channelNames:
     for sampleName in data[channelName]:
       if not re.search(sampleMustBe,sampleName):
         continue
       for errName in data[channelName][sampleName]:
         if mustMatchList != None:
            if not matches(errName, mustMatchList):
              continue
         if cantMatchList != None:
            if matches(errName, cantMatchList):
              continue
         if errName == "nom":
            continue
         if niceTitles:
           errName = errNameMap[errName]
         errNames.append(errName)
         errNamesString += "{"+str(iErrName)+":^"+str(len(errName)+2)+"}"
         if latex:
           errNamesString += "&"
         iErrName += 1
     break
  if latex:
    errNamesString = errNamesString.rstrip("&")
    errNamesString += r"\\ \hline \hline"
  errNamesString = errNamesString.format(*errNames)
  outString += "\n"+errNamesString+"\n"
  for channelName in channelNames:
    errVals = [channelName]
    if niceTitles:
      errVals = [channelNameMap[channelName]]
    errVals2 = [""]
    errValsString = "{0:<"+maxChannelWidth+"}"
    errValsString2 = "{0:<"+maxChannelWidth+"}"
    if latex:
      errValsString += r"&"
      errValsString2 += r"&"
    iErrVal = 1
    for sampleName in data[channelName]:
      if not re.search(sampleMustBe,sampleName):
         continue
      for errName in data[channelName][sampleName]:
        if mustMatchList != None:
            if not matches(errName, mustMatchList):
              continue
        if cantMatchList != None:
            if matches(errName, cantMatchList):
              continue
        if errName == "nom":
            continue
        errVals.append("+{0:.3%}".format(data[channelName][sampleName][errName]["Up"]))
        errVals2.append("-{0:.3%}".format(data[channelName][sampleName][errName]["Down"]))
        if niceTitles:
            errName = errNameMap[errName]
        errValsString += "{"+str(iErrVal)+":^"+str(len(errName)+2)+"}"
        errValsString2 += "{"+str(iErrVal)+":^"+str(len(errName)+2)+"}"
        if latex:
           errValsString += "&"
           errValsString2 += "&"
        iErrVal += 1
    errValsString = errValsString.format(*errVals)
    errValsString2 = errValsString2.format(*errVals2)
    if latex:
      errValsString = errValsString.rstrip("&")
      errValsString2 = errValsString2.rstrip("&")
      errValsString += r"\\"
      errValsString2 += r"\\ \hline"
    errValsString += "\n"+errValsString2+"\n"
    outString += errValsString

  if latex:
    columnFormat = "|l|" + "c|"*len(errNames)
    outString = r"\begin{tabular}{"+columnFormat+"} \hline" + outString + r"\end{tabular}"+"\n"
    outString = outString.replace(r"%",r"\%")

  return outString
    
if __name__ == "__main__":
 import subprocess
 import os
  
 ggFileName = "input/ggHmumu125_8TeV.root"
 vbfFileName = "input/vbfHmumu125_8TeV.root"
 dataDir = "statsCards/"
 #filenames = ["statsCards/BDTCut_8TeV_20.root"]
 filenames = ["statsCards/BDTCutCat_8TeV_20.root"]
 #filenames = glob.glob(dataDir+"20*.root")

 for fn in filenames:
  sPlotter = makeShapePlots.ShapePlotter(fn,makeShapePlots.titleMap,doSignalScaling=False)
    
  counts = convertHistToCounts(sPlotter.data,ggFileName,vbfFileName)
  shapeErrors = getShapeErrorsFromCounts(counts)

  samples = ["sig","bak"]
  titles = ["Signal","Background"]
  for i, title in zip(samples,titles):

    f = open("tableErrors"+title+".tex","w")
    #f.write(writeErrorTable(shapeErrors,True,True,mustMatchList=["TotalSyst"]))
    f.write(writeErrorTable(shapeErrors,True,True,sampleMustBe=i,cantMatchList=["br_","xs_"]))
    f.close()

  f = open("tableErrorsTest.tex","w")
  testStr = r"""
\documentclass[12pt,a4paper]{article}
\usepackage{lscape}
\begin{document}
\begin{landscape}
%\tiny
\small

"""
  for t in titles:
    testStr += r"\input{tableErrors"+t+"}\n \\\\ \n"
  testStr += r"""

\end{landscape}
\end{document}
"""
  f.write(testStr)
  f.close()
  subprocess.call(["latex","tableErrorsTest.tex"])
  subprocess.call(["dvipdf","tableErrorsTest.dvi"])
  os.remove("tableErrorsTest.aux")
  os.remove("tableErrorsTest.log")
  os.remove("tableErrorsTest.dvi")

  for i in shapeErrors:
    print(i)
    for j in shapeErrors[i]:
      print("  {}".format(j))
      for k in shapeErrors[i][j]:
        print("    {} {}".format(k,shapeErrors[i][j][k]))

  for i in sPlotter.data:
    print(i)
    for j in sPlotter.data[i]:
      tmp = sPlotter.data[i][j]
      print("  {}: {}".format(j,tmp.Integral()))
