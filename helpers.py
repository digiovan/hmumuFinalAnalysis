
import ROOT as root
from ROOT import gStyle as gStyle
#from ROOT import RooRealVar, RooGaussian, RooArgList, RooDataHist
import re
import csv
import glob
from math import sqrt
import numpy
import array
import sys
import matplotlib.pyplot as mpl

#PRELIMINARYSTRING="CMS Internal"
PRELIMINARYSTRING="CMS Preliminary"
#PRELIMINARYSTRING="CMS"

def fit2DResHist(hist,color):
  histName = hist.GetName()
  hist.FitSlicesY()
  outMeanHist = root.gDirectory.Get(histName+"_1")
  outSigmaHist = root.gDirectory.Get(histName+"_2")

  outMeanHist.SetName(histName+"FitMean")
  outSigmaHist.SetName(histName+"FitSigma")
  outMeanHist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
  outSigmaHist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
  outMeanHist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())
  outSigmaHist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())

  outSigOverMeanHist = outSigmaHist.Clone(histName+"FitSigmaOverMean")
  outSigOverMeanHist.Divide(outMeanHist)

  outMeanHist.SetMarkerColor(color)
  outMeanHist.SetLineColor(color)
  outSigmaHist.SetMarkerColor(color)
  outSigmaHist.SetLineColor(color)
  outSigOverMeanHist.SetMarkerColor(color)
  outSigOverMeanHist.SetLineColor(color)

  outMeanHist.SetTitle("")
  outSigmaHist.SetTitle("")
  outSigOverMeanHist.SetTitle("")

  return outMeanHist, outSigmaHist, outSigOverMeanHist

class Fit1DResHist:
  def __init__(self,hist1,hist2,canvas,fitList=[0.9,1.1],xlimits=[0.5,1.5],captions=[]):
    histName1 = hist1.GetName()

    self.captions = captions

    self.canvas = canvas
    canvas.cd()

    self.hist1 = hist1
    self.hist2 = hist2

    tlatex = root.TLatex()
    tlatex.SetNDC()
    tlatex.SetTextSize(0.035)
    tlatex.SetTextAlign(12)
    self.tlatex = tlatex
  
    gaus1 = root.TF1("gaus1"+histName1,"gaus",fitList[0],fitList[1])
    gaus2 = root.TF1("gaus2"+histName1,"gaus",fitList[0],fitList[1])
    gaus1.SetLineColor(root.kBlack)
    gaus2.SetLineColor(root.kRed+1)
    self.gaus1 = gaus1
    self.gaus2 = gaus2

    hist1.Fit(gaus1,"WLMEIQ","",fitList[0],fitList[1])
    hist2.Fit(gaus2,"WLMEIQ","",fitList[0],fitList[1])

    hist1.GetXaxis().SetRangeUser(*xlimits)
    hist1.GetXaxis().SetTitle("p_{T}^{X}/p_{T}^{True}")
    
    hist1.SetLineColor(1)
    hist1.SetMarkerColor(1)
    hist2.SetLineColor(root.kRed+1)
    hist2.SetMarkerColor(root.kRed+1)
    hist1.Draw()
    hist2.Draw("same")
    
    tlatex.SetTextAlign(12)
    tlatex.SetTextSize(0.022)
    #tlatex.DrawLatex(0.65,0.55,"Mean_{RECO} = %.3f" % 
    #        (gaus1.GetParameter(1)))
    #tlatex.DrawLatex(0.65,0.5,"Mean_{Regr.} = %.3f" % 
    #        (gaus2.GetParameter(1)))
    #tlatex.DrawLatex(0.65,0.45,"#sigma_{RECO} = %.3f" % 
    #        (gaus1.GetParameter(2)))
    #tlatex.DrawLatex(0.65,0.4,"#sigma_{Regr.} = %.3f" % 
    #        (gaus2.GetParameter(2)))
    tlatex.DrawLatex(0.65,0.55,"Mean_{RECO} = %.3f #pm %.3f" % 
            (gaus1.GetParameter(1),gaus1.GetParError(1)))
    tlatex.DrawLatex(0.65,0.5,"Mean_{Regr.} = %.3f #pm %.3f" % 
            (gaus2.GetParameter(1),gaus2.GetParError(1)))
    tlatex.DrawLatex(0.65,0.45,"#sigma_{RECO} = %.3f #pm %.3f" % 
            (gaus1.GetParameter(2),gaus1.GetParError(2)))
    tlatex.DrawLatex(0.65,0.4,"#sigma_{Regr.} = %.3f #pm %.3f" % 
            (gaus2.GetParameter(2),gaus2.GetParError(2)))
    
    tlatex.SetTextSize(0.035)
    i = 0.85
    mini = 0.3
    for el in captions:
        tlatex.DrawLatex(0.2,i,el)
        i = i - 0.05
        if(i<mini):
            break

def fit2DResHistManual(hist,color,fitDictList=[],xlimits=[0.0,2.0]):
  histName = hist.GetName()
  histSaveName = "slices_"+histName+".pdf"

  outMeanHist = hist.ProjectionX()
  outMeanHist.Clear()
  outMeanHist.Sumw2()
  outMeanHist.SetName(histName+"FitMean")
  outSigmaHist = outMeanHist.Clone(histName+"FitSigma")
  outRMSHist = outMeanHist.Clone(histName+"FitRMS")

  tmpCanvas = root.TCanvas("tmpCanvas"+histName)
  tmpCanvas.cd()
  tmpCanvas.SetGridx(1)
  tlatex = root.TLatex()
  tlatex.SetNDC()
  tlatex.SetTextSize(0.035)
  tlatex.SetTextAlign(12)

  nBins = hist.GetXaxis().GetNbins()
  for i in range(0,nBins+2):
    sliceHist = getXBinHist(hist,i)

    mean = sliceHist.GetMean()
    meanErr = sliceHist.GetMeanError()
    rms = sliceHist.GetRMS()
    rmsErr = sliceHist.GetRMSError()

    maxBin = sliceHist.GetMaximumBin()
    xMax = sliceHist.GetXaxis().GetBinCenter(maxBin)
    gaus = root.TF1("gaus","gaus");
    if fitDictList==[]:
      sliceHist.Fit(gaus,"WLMEIQ","",xMax-0.2,xMax+0.2)
    else:
      sliceHist.Fit(gaus,"WLMEIQ","",fitDictList[i][0],fitDictList[i][1])
    sliceHist.SetTitle("pt: "+str(hist.GetXaxis().GetBinCenter(i))+"   iBin: "+str(i))
    sliceHist.GetXaxis().SetRangeUser(*xlimits)
    sliceHist.Draw()

    # 1 is mean, 2 is sigma
    fitMean = gaus.GetParameter(1)
    fitMeanErr = gaus.GetParError(1)
    fitSig = gaus.GetParameter(2)
    fitSigErr = gaus.GetParError(2)
    fitChi2 = gaus.GetChisquare()
    fitNDF = gaus.GetNDF()
    if fitMean ==0.0:
        fitMean = 1.0e-10
    if fitSig ==0.0:
        fitSig = 1.0e-10
    if rms ==0.0:
        rms = 1.0e-10
    outMeanHist.SetBinContent(i,fitMean)
    outMeanHist.SetBinError(i,fitMeanErr)
    outSigmaHist.SetBinContent(i,fitSig/fitMean)
    outSigmaHist.SetBinError(i,fitSig/fitMean*sqrt((fitSigErr/fitSig)**2+(fitMeanErr/fitMean)**2))
    outRMSHist.SetBinContent(i,rms/fitMean)
    outRMSHist.SetBinError(i,rms/fitMean*sqrt((rmsErr/rms)**2+(fitMeanErr/fitMean)**2))

    """
    outMeanHist.SetBinContent(i,mean)
    outMeanHist.SetBinError(i,meanErr)
    outSigmaHist.SetBinContent(i,rms)
    outSigmaHist.SetBinError(i,rmsErr)
    """

    """
    ptDiff = RooRealVar("ptDiff","pt - pt",hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    mean1 = RooRealVar("mean1","<pt-pt>",0.0)
    sigma1 = RooRealVar("sigma1","#sigma(pt-pt)",5.0)
    mean1.setConstant(False)
    sigma1.setConstant(False)

    frame1 = ptDiff.frame()

    gaus1 = RooGaussian("guas1","Guassian",ptDiff,mean1,sigma1)
    data = RooDataHist("data","Data",RooArgList(ptDiff),sliceHist)
    gaus1.fitTo(data)

    data.plotOn(frame1)
    gaus1.plotOn(frame1)

    outMeanHist.SetBinContent(i,mean1.GetVal())
    outMeanHist.SetBinError(i,mean1.GetError())
    outSigmaHist.SetBinContent(i,sigma1.GetVal())
    outSigmaHist.SetBinError(i,sigma1.GetError())

    frame1.SetTitle("pt: "+str(hist.GetXaxis().GetBinCenter(i))+"   iBin: "+str(i))
    frame1.GetXaxis().SetRangeUser(-100,100)
    frame1.Draw()
    """

    tlatex.DrawLatex(0.6,0.75,"Mean: %.3f #pm %.3f" % (fitMean,fitMeanErr))
    tlatex.DrawLatex(0.6,0.8,"#sigma: %.3f #pm %.3f" % (fitSig,fitSigErr))
    tlatex.DrawLatex(0.6,0.7,"#chi/NDF: %.3f / %.3f" % (fitChi2,fitNDF))
    if(i == 0):
	  tmpCanvas.SaveAs(histSaveName+"(")
	  tmpCanvas.Clear()
    elif(i == nBins+1):
	  tmpCanvas.SaveAs(histSaveName+")")
	  tmpCanvas.Clear()
    else:
	  tmpCanvas.SaveAs(histSaveName)
	  tmpCanvas.Clear()

  outMeanHist.SetMarkerColor(color)
  outMeanHist.SetLineColor(color)
  outSigmaHist.SetMarkerColor(color)
  outSigmaHist.SetLineColor(color)
  outRMSHist.SetMarkerColor(color)
  outRMSHist.SetLineColor(color)
  outMeanHist.SetTitle("")
  outSigmaHist.SetTitle("")
  outRMSHist.SetTitle("")

  #outMeanHist.Print()
  #outSigmaHist.Print()
  #outRMSHist.Print()

  return outMeanHist, outSigmaHist, outRMSHist

def getXBinHist(inHist, xBin):
  outHist = inHist.ProjectionY()
  outHist.Clear()
  outHist.SetName(inHist.GetName()+"XSliceBin"+str(xBin))
  outHist.Sumw2()
  nBins = outHist.GetXaxis().GetNbins()
  for i in range(0,nBins+2):
    outHist.SetBinContent(i,inHist.GetBinContent(xBin,i))
    outHist.SetBinError(i,inHist.GetBinError(xBin,i))
  return outHist

def getYBinHist(inHist, yBin):
  outHist = inHist.ProjectionX()
  outHist.Clear()
  outHist.SetName(inHist.GetName()+"YSliceBin"+str(yBin))
  outHist.Sumw2()
  nBins = outHist.GetYaxis().GetNbins()
  for i in range(0,nBins+2):
    outHist.SetBinContent(i,inHist.GetBinContent(i,yBin))
    outHist.SetBinError(i,inHist.GetBinError(i,yBin))
  return outHist

def fitSlicesTopRooFit(hist):
  #mTopBest = 172.9
  mass = root.RooRealVar("mass","m_{jjj} of Top Candidate [GeV]",20,250)
  #mtParam = root.RooRealVar("mtParam","m_{t} Parameter",mTopBest);
  #wtParam = root.RooRealVar("wtParam","#Gamma_{t} Parameter",2.0);

  smearMeanParam = root.RooRealVar("smearMeanParam","m_{t} Smearing Mean",0.0);
  smearSigParam = root.RooRealVar("smearSigParam","m_{t} Smearing Sigma",0.5);

  smearMeanParam.setConstant(False);
  smearSigParam.setConstant(False);

  #bwPdf = root.RooBreitWigner("bwPdf","m_{t} Breit-Wigner Pdf",
  #						mass,mtParam,wtParam);
  smearPdf = root.RooGaussian("smearPdf","m_{t} Smearing PDF",
						mass,smearMeanParam,smearSigParam);
  #convPdf = root.RooFFTConvPdf("convPdf","m_{t} Convolution of BW with Gaussian",
  #						mass,bwPdf,smearPdf);

  outMeanGraph = root.TGraphErrors()
  outSigGraph = root.TGraphErrors()
  if(hist.GetDimension()==1):
      
      mass = root.RooRealVar("mass","m_{jjj} of Top Candidate [GeV]",hist.GetXaxis().GetXmin(),hist.GetXaxis().GetXmax())
      smearMeanParam = root.RooRealVar("smearMeanParam","m_{t} Smearing Mean",0.0);
      smearSigParam = root.RooRealVar("smearSigParam","m_{t} Smearing Sigma",0.5);
      smearMeanParam.setConstant(False);
      smearSigParam.setConstant(False);
      smearPdf = root.RooGaussian("smearPdf","m_{t} Smearing PDF",
						mass,smearMeanParam,smearSigParam);

      data = root.RooDataHist("data",
  			"t Candidate m_{jjj} from Measured b-jet and Fit W-mass",
  			root.RooArgList(mass),hist)
  
      smearPdf.fitTo(data)
                                                                            
      smearMean = smearMeanParam.getVal()
      smearMeanErr = smearMeanParam.getError()
      smearSig = smearSigParam.getVal()
      smearSigErr = smearSigParam.getError()
      return smearMean, smearMeanErr, smearSig, smearSigErr

  elif(hist.GetDimension()==2):
    iPoint=0;
    nBinsX = hist.GetXaxis().GetNbins()
    for iBinX in range(1,nBinsX+1):
      dataHist = getXBinHist(hist,iBinX);
      dataHist.Rebin(2)
      data = root.RooDataHist("data",
  			"t Candidate m_{jjj} from Measured b-jet and Fit W-mass",
  			root.RooArgList(mass),dataHist)
  
      print("justin bin: "+str(iBinX))
      dataHist.Print("v")
      data.Print("v")
      fitResult = convPdf.fitTo(data,root.RooFit.Save())
                                                                            
      smearMean = smearMeanParam.getVal()
      smearMeanErr = smearMeanParam.getError()
      smearSig = smearSigParam.getVal()
      smearSigErr = smearSigParam.getError()
  
      xPos = hist.GetXaxis().GetBinCenter(iBinX)
      xErr = hist.GetXaxis().GetBinWidth(iBinX)/2.0
  
      #should it be divided by mTopBest or xPos?
      smearSig = smearSig/xPos
      smearSigErr = smearSigErr/xPos
      smearMean = smearMean/xPos
      smearMeanErr = smearMeanErr/xPos
      """
      outMeanGraph.SetPoint(iPoint,xPos,dataHist.GetMean())
      outMeanGraph.SetPointError(iPoint,xErr,dataHist.GetMeanError())
      smearSig = dataHist.GetRMS()/mTopBest
      smearSigErr = dataHist.GetRMSError()/mTopBest
      """
  
      outMeanGraph.SetPoint(iPoint,xPos,smearMean)
      outMeanGraph.SetPointError(iPoint,xErr,smearMeanErr)
      outSigGraph.SetPoint(iPoint,xPos,smearSig)
      outSigGraph.SetPointError(iPoint,xErr,smearSigErr)
  
      iPoint = iPoint+1

  return outMeanGraph, outSigGraph

def divideYValByXVal(hist):
    nBinsX = hist.GetXaxis().GetNbins()
    for iBinX in range(1,nBinsX+1):
	binVal = hist.GetBinContent(iBinX)
	binErrVal = hist.GetBinError(iBinX)
	xVal = hist.GetXaxis().GetBinCenter(iBinX)
	hist.SetBinContent(iBinX,binVal/xVal)
	hist.SetBinError(iBinX,binErrVal/xVal)

def drawMVAHist(tfile, histToGetRE, meanOrsigmaString):
  """
   Draws a hist from the TMVA out file.  Must already have an active TCanvas
  """
  leg = root.TLegend(0.70,0.6,0.9,0.9)
  leg.SetFillColor(root.kWhite)
  leg.SetLineColor(root.kWhite)
  colors = [root.kBlack,root.kBlue+1,root.kRed+1,root.kBlue+1,root.kOrange+1]
  iColor = 0
  for dirName in tfile.GetListOfKeys():
   if(re.match(r"Method_.*",dirName.GetName())):
     for subDirName in dirName.ReadObj().GetListOfKeys():
       for histName in subDirName.ReadObj().GetListOfKeys():
	if(re.match(histToGetRE,histName.GetName())):
	  hist = histName.ReadObj()
	  #hist.GetXaxis().Rebin(2)
	  hM, hS, hSOM = fit2DResHist(hist)
	  hM.SetLineColor(colors[iColor % len(colors)])
	  hM.SetMarkerColor(colors[iColor % len(colors)])
	  hS.SetLineColor(colors[iColor % len(colors)])
	  hS.SetMarkerColor(colors[iColor % len(colors)])
	  hSOM.SetLineColor(colors[iColor % len(colors)])
	  hSOM.SetMarkerColor(colors[iColor % len(colors)])
	  tmpLegLabel = re.sub(r"MVA_","",histName.GetName())
	  tmpLegLabel = re.sub(r"test.*","",tmpLegLabel)
	  leg.AddEntry(hM,tmpLegLabel,"lep")
	  divideYValByXVal(hS)
	  
	  if(iColor==0):
	    if(meanOrsigmaString == "mean"):
		hM.SetTitle("")
		hM.GetYaxis().SetRangeUser(-10,10)
		hM.Draw()
	    else:
		hS.SetTitle("")
		hS.GetYaxis().SetRangeUser(0.0,0.6)
		hS.Draw()
	  else:
	    if(meanOrsigmaString == "mean"):
		hM.Draw("same")
	    else:
		hS.Draw("same")
	  iColor += 1
  leg.Draw()
  leg.Print()
  print("made it to leg.Draw")

def makeResPlotFromMVATree(tfile,xname,yname,truename,cuts,doDivide):
  histName2D = "mvaResTmpHist"
  tree = tfile.Get("TestTree")
  #tree = tfile.Get("TrainTree")
  drawStr = ""
  if doDivide:
    drawStr = "("+yname+"-"+truename+")/"+truename+":"+xname
  else:
    drawStr = yname+"-"+truename+":"+xname
  drawStr += ">>"
  drawStr += histName2D
  print(drawStr)
  tree.Draw(drawStr,cuts)
  tmpHist = root.gDirectory.Get(histName2D)
  tmpM, tmpS, tmpSOM = fit2DResHist(tmpHist,root.kBlack)
  if(doDivide):
    tmpM.GetYaxis().SetRangeUser(-1,1)
    tmpS.GetYaxis().SetRangeUser(0,0.5)
  else:
    tmpM.GetYaxis().SetRangeUser(-50,50)
    tmpS.GetYaxis().SetRangeUser(0,100)
  tmpM.SetTitle("")
  tmpS.SetTitle("")
  return tmpM, tmpS



def setStyle():
  gStyle.SetCanvasColor(0)
  gStyle.SetCanvasBorderSize(10)
  gStyle.SetCanvasBorderMode(0)
  gStyle.SetCanvasDefH(700)
  gStyle.SetCanvasDefW(700)

  gStyle.SetPadColor       (0)
  gStyle.SetPadBorderSize  (10)
  gStyle.SetPadBorderMode  (0)
  gStyle.SetPadBottomMargin(0.13)
  gStyle.SetPadTopMargin   (0.08)
  gStyle.SetPadLeftMargin  (0.15)
  gStyle.SetPadRightMargin (0.05)
  gStyle.SetPadGridX       (0)
  gStyle.SetPadGridY       (0)
  gStyle.SetPadTickX       (1)
  gStyle.SetPadTickY       (1)

  gStyle.SetFrameFillStyle ( 0)
  gStyle.SetFrameFillColor ( 0)
  gStyle.SetFrameLineColor ( 1)
  gStyle.SetFrameLineStyle ( 0)
  gStyle.SetFrameLineWidth ( 1)
  gStyle.SetFrameBorderSize(10)
  gStyle.SetFrameBorderMode( 0)

  gStyle.SetNdivisions(505)

  gStyle.SetLineWidth(2)
  gStyle.SetHistLineWidth(2)
  gStyle.SetFrameLineWidth(2)
  gStyle.SetLegendFillColor(root.kWhite)
  gStyle.SetLegendFont(42)
  gStyle.SetMarkerSize(1.2)
  gStyle.SetMarkerStyle(20)
 
  gStyle.SetLabelSize(0.040,"X")
  gStyle.SetLabelSize(0.040,"Y")

  gStyle.SetLabelOffset(0.010,"X")
  gStyle.SetLabelOffset(0.010,"Y")
 
  gStyle.SetLabelFont(42,"X")
  gStyle.SetLabelFont(42,"Y")
 
  gStyle.SetTitleBorderSize(0)
  gStyle.SetTitleFont(42)
  gStyle.SetTitleFont(42,"X")
  gStyle.SetTitleFont(42,"Y")

  gStyle.SetTitleSize(0.045,"X")
  gStyle.SetTitleSize(0.045,"Y")
 
  gStyle.SetTitleOffset(1.4,"X")
  gStyle.SetTitleOffset(1.4,"Y")
 
  gStyle.SetTextSize(0.055)
  gStyle.SetTextFont(42)
 
  gStyle.SetOptStat(0)

setStyle()

def setHistTitles(hist,xlabel,ylabel):
    hist.GetXaxis().SetTitle(xlabel)
    hist.GetYaxis().SetTitle(ylabel)

def makeWeightHist(f1,canvas,leg):
  firstHist = True
  canvas.cd()
  canvas.SetLogy()
  colorsList = [1,2,3,4,5,6,7,8]
  nColors = len(colorsList)
  iDir = 0
  leg.Clear()
  leg.SetFillColor(0)
  leg.SetLineColor(0)
  tmpList = []
  for dirName in f1.GetListOfKeys():
    tmpList.append(dirName)
  tmpList.reverse()
  for dirName in tmpList:
    print(dirName.GetName())
    if(re.search(r"data",dirName.GetName())):
	continue
    directory = dirName.ReadObj()
    for histKey in directory.GetListOfKeys():
      if(histKey.GetName()=="hWeight"):
        hist = histKey.ReadObj()
	hist.UseCurrentStyle()
	hist.SetLineColor(colorsList[iDir % nColors])
	hist.SetMarkerColor(colorsList[iDir % nColors])
	allIntegral = hist.Integral(0,hist.GetNbinsX()+1)
	integral = hist.Integral()
	if integral > 0.0:
	  print("Fraction Outside of bounds: %f" % (allIntegral/integral-1.0))
	  #hist.Scale(1.0/allIntegral)
	  hist.Scale(1.0/integral)
	else:
	  leg.AddEntry(hist,dirName.GetName(),"lep")
	if(firstHist):
	  firstHist=False
	  hist.GetYaxis().SetTitle("Fraction of Events")
	  hist.GetXaxis().SetTitle("Event Weight")
	  #hist.GetXaxis().SetRangeUser(0.0,1.0)
	  hist.Draw()
	else:
	  hist.Draw("same")
    iDir += 1
  leg.Draw("same")

class DataMCStack:
  def __init__(self, mcHistList, dataHist, canvas, xtitle, ytitle="", drawStack=True,nDivX=7,xlimits=[],showOverflow=False,lumi=5.0,logy=False,signalsNoStack=[],showCompatabilityTests=True,integralPlot=False,energyStr="8TeV",ylimits=[],ylimitsRatio=[],pullType="",doMCErrors=False,showPullStats=False):
    nBinsX = dataHist.GetNbinsX()
    self.nBinsX = nBinsX
    self.dataHist = dataHist
    self.canvas = canvas
    self.tlatex = root.TLatex()
    self.tlatex.SetNDC()
    self.tlatex.SetTextFont(root.gStyle.GetLabelFont())
    self.tlatex.SetTextSize(0.05)
    self.tlatex.SetTextAlign(22)
    if ytitle=="":
      ytitle="Events/{0}".format(getBinWidthStr(dataHist))
    for mcHist in mcHistList:
      #print("nBinsX data: %i, mc: %i" % (nBinsX,mcHist.GetNbinsX()))
      assert(nBinsX == mcHist.GetNbinsX())
    for sigHist in signalsNoStack:
      assert(nBinsX == sigHist.GetNbinsX())

    if integralPlot:
      dataHist = getIntegralHist(dataHist,True)
      self.dataHist = dataHist
      newMcHistList = []
      for i in mcHistList:
        newMcHistList.append(getIntegralHist(i))
      mcHistList = newMcHistList
      newSigHistList = []
      for i in signalsNoStack:
        newSigHistList.append(getIntegralHist(i))
      signalsNoStack = newSigHistList
      ytitle = "Integral of "+ytitle+" #geq X"
    self.signalsNoStack = signalsNoStack
    self.mcHistList = mcHistList
    self.dataHist = dataHist
  
    # Make MC Stack/sumHist
    self.stack = root.THStack()
    self.mcSumHist = dataHist.Clone("mcSumHist"+dataHist.GetName())
    self.mcSumHist.Reset()
    for mcHist in mcHistList:
      mcHist.SetMaximum(1e12)
      mcHist.SetMinimum(1e-12)
      mcHist.SetLineColor(mcHist.GetFillColor())
      if showOverflow:
        showHistOverflow(mcHist)
      self.mcSumHist.Add(mcHist)
      self.stack.Add(mcHist)

    if showOverflow:
        showHistOverflow(dataHist)

    self.mcSumHist.SetFillColor(root.kGray+3)
    self.mcSumHist.SetFillStyle(3013)
    self.mcSumHist.SetMarkerSize(0)
    if doMCErrors and drawStack:
        self.mcSumHist.SetLineStyle(0)

    self.nMCEvents = self.mcSumHist.Integral(0,self.mcSumHist.GetNbinsX()+1)
    self.nDataEvents = dataHist.Integral(0,dataHist.GetNbinsX()+1)

    # Get chi^2 Prob Data/MC
    self.normchi2 = dataHist.Chi2Test(self.mcSumHist,"UW CHI2/NDF")
    self.chi2Prob = dataHist.Chi2Test(self.mcSumHist,"UW")
    self.KSProb = dataHist.KolmogorovTest(self.mcSumHist)
    if self.chi2Prob < 1e-20:
        self.chi2Prob = 0.0
    if self.KSProb < 1e-20:
        self.KSProb = 0.0

    # Make Pull Hist
    self.pullList = []
    self.pullHist = dataHist.Clone("pullHist"+dataHist.GetName())
    self.pullHist.Reset()
    self.oneGraph = root.TGraph()
    self.oneGraph.SetLineWidth(2)
    self.oneGraph.SetLineStyle(2)
    iGraph = 0
    for i in range(0,self.pullHist.GetNbinsX()+2):
      nData = dataHist.GetBinContent(i)
      nMC = self.mcSumHist.GetBinContent(i)
      error = dataHist.GetBinError(i)
      errorMC = self.mcSumHist.GetBinError(i)
      pull = 0.0
      ratio = 0.0
      ratioErr = 0.0
      self.oneGraph.SetPoint(iGraph,dataHist.GetXaxis().GetBinCenter(i),1.0)
      iGraph += 1
      if error != 0.0:
        if pullType=="adrian1":
          pull = (nData -nMC)/nData
        else:
          pull = (nData -nMC)/error
      if pullType=="pullMC":
        if errorMC != 0.0:
          pull = (nData -nMC)/errorMC
        else:
          pull = 0.0
      if nMC != 0.0:
        ratio = nData/nMC
        ratioErr = error/nMC
      if pullType=="ratio":
        self.pullHist.SetBinContent(i,ratio)
        self.pullHist.SetBinError(i,ratioErr)
        #print("nData: {0:.2f} +/- {1:.2f}, nMC: {2:.2f}, ratio: {3:.2f} +/- {4:.2f}".format(nData,error,nMC,ratio,ratioErr))
      else:
        self.pullHist.SetBinContent(i,pull)
        #print("nData: %f, nMC: %f, error: %f, pull: %f" % (nData,nMC,error,pull))
      #pullDistribution
      if pullType == "pullMC":
        if errorMC != 0.0:
          self.pullList.append((nData -nMC)/errorMC)
      else:
        if error != 0.0:
          self.pullList.append((nData -nMC)/error)
    #print getattr(self,"getPullDistributionParams")(self.pullList)

    #Find Maximum y-value
    if xlimits != []:
      self.mcSumHist.GetXaxis().SetRangeUser(*xlimits)
      self.dataHist.GetXaxis().SetRangeUser(*xlimits)
    mcMax = self.mcSumHist.GetMaximum()
    dataMaxBin = self.dataHist.GetMaximumBin()
    dataMax = dataHist.GetBinContent(dataMaxBin)+dataHist.GetBinError(dataMaxBin)
    ymax = 0.0
    if mcMax > dataMax:
       ymax = mcMax
    else:
       ymax = dataMax
    self.ymax = ymax
  
    #Setup Canvas
    canvas.cd()
    pad1 = root.TPad("pad1"+dataHist.GetName(),"",0.02,0.30,0.98,0.98,0)
    pad2 = root.TPad("pad2"+dataHist.GetName(),"",0.02,0.01,0.98,0.29,0)
    self.pad1 = pad1
    self.pad2 = pad2
  
    pad1.SetBottomMargin(0.005);
    pad2.SetTopMargin   (0.005);
    pad2.SetBottomMargin(0.33);
    """
    pad1.SetBottomMargin(0.01);
    pad2.SetTopMargin   (0.3);
    pad2.SetBottomMargin(0.33);
    """
    canvas.SetLogy(0)
    pad2.SetLogy(0)
    if logy:
        pad1.SetLogy(1)
    else:
        pad1.SetLogy(0)
  
    pad1.Draw() # Projections pad
    pad2.Draw() # Residuals   pad

    pad1Width = pad1.XtoPixel(pad1.GetX2())
    pad1Height = pad1.YtoPixel(pad1.GetY1())
    pad2Height = pad2.YtoPixel(pad2.GetY1())
    #pad1ToPad2FontScalingFactor = float(pad1Width)/pad2Height
    pad1ToPad2FontScalingFactor = float(pad1Height)/pad2Height
  
    # Main Pad
    pad1.cd();
    xAxis = None
    yAxis = None
    if drawStack:
      self.stack.Draw("hist")
      if xlimits != []:
        self.stack.GetXaxis().SetRangeUser(*xlimits)
      self.stack.GetXaxis().SetTitle("")
      self.stack.GetXaxis().SetLabelSize(0)
      self.stack.GetYaxis().SetTitle(ytitle)
      self.stack.GetYaxis().SetLabelSize(0.050)
      self.stack.GetYaxis().SetTitleSize(0.055)
      self.stack.GetXaxis().SetNdivisions(nDivX)
      self.stack.SetMaximum(ymax*1.00)
      if logy:
        self.stack.SetMinimum(0.1)
        if len(ylimits) == 2:
          self.stack.SetMaximum(ylimits[1]*0.47)
          self.stack.SetMinimum(ylimits[0])
          if logy and ylimits[0]==0.0:
            self.stack.SetMinimum(0.1)
      else:
        if len(ylimits) == 2:
          self.stack.SetMaximum(ylimits[1]*0.95)
          self.stack.SetMinimum(ylimits[0])
      self.stack.Draw("hist")
      if doMCErrors:
        self.mcSumHist.Draw("e2same")
      pad1.Update()
    else:
      self.mcSumHist.SetFillColor(856)
      self.mcSumHist.SetLineColor(856)
      self.mcSumHist.SetMarkerColor(856)
      self.mcSumHist.SetFillStyle(1001)
      self.mcSumHist.SetTitle("")
      self.mcSumHist.GetXaxis().SetTitle("")
      self.mcSumHist.GetXaxis().SetLabelSize(0)
      self.mcSumHist.GetYaxis().SetTitle(ytitle)
      self.mcSumHist.GetYaxis().SetLabelSize(0.050)
      self.mcSumHist.GetYaxis().SetTitleSize(0.055)
      self.mcSumHist.GetXaxis().SetNdivisions(nDivX)
      if logy:
        self.mcSumHist.GetYaxis().SetRangeUser(1.0,ymax*1.04)
      else:
        self.mcSumHist.GetYaxis().SetRangeUser(0.0,ymax*1.04)
      if xlimits != []:
        self.mcSumHist.GetXaxis().SetRangeUser(*xlimits)
      if len(ylimits) == 2:
        self.stack.GetYaxis().SetRangeUser(*ylimits)
      self.mcSumHist.Draw("histo b")
    for sigHist in signalsNoStack:
      sigHist.Draw("histo same")
    dataHist.Draw("pe same")

    pad1.RedrawAxis() # Updates Axis Lines
  
    # Pulls Pad
    pad2.cd()
    self.pullHist.SetTitle("")
    if xlimits != []:
      self.pullHist.GetXaxis().SetRangeUser(*xlimits)
    self.pullHist.GetXaxis().SetTitle(xtitle)
    self.pullHist.GetXaxis().CenterTitle(1)
    self.pullHist.GetXaxis().SetNdivisions(nDivX)
    self.pullHist.GetXaxis().SetTitleSize(0.055*pad1ToPad2FontScalingFactor)
    self.pullHist.GetXaxis().SetLabelSize(0.050*pad1ToPad2FontScalingFactor)
    self.pullHist.SetLineColor(root.kBlue)
    self.pullHist.SetLineStyle(1)
    self.pullHist.SetLineWidth(2)
    if pullType=="adrian1":
      self.pullHist.GetYaxis().SetTitle("#frac{Data-MC}{Data}")
    elif pullType=="pullMC":
      self.pullHist.GetYaxis().SetTitle("#frac{Data-MC}{\sigma_{MC}}")
    else:
      self.pullHist.GetYaxis().SetTitle("#frac{Data-MC}{\sigma_{Data}}")
    self.pullHist.GetYaxis().SetTitleSize(0.040*pad1ToPad2FontScalingFactor)
    self.pullHist.GetYaxis().SetLabelSize(0.040*pad1ToPad2FontScalingFactor)
    self.pullHist.GetYaxis().CenterTitle(1)
    self.pullHist.GetXaxis().SetTitleOffset(0.75*self.pullHist.GetXaxis().GetTitleOffset())
    self.pullHist.GetYaxis().SetTitleOffset(0.70)
    self.pullHist.SetFillColor(856)
    self.pullHist.SetFillStyle(1001)
    if len(ylimitsRatio) == 2:
      self.pullHist.GetYaxis().SetRangeUser(*ylimitsRatio)

    if pullType=="ratio":
      #pad2.SetGridy(1)
      self.pullHist.GetYaxis().SetTitle("#frac{Data}{MC}")
      self.pullHist.Draw("")
      self.oneGraph.Draw()
      self.pullHist.Draw("same")
    else:
      self.pullHist.Draw("histo")

    if showCompatabilityTests:
      self.problatex = root.TLatex()
      self.problatex.SetNDC()
      self.problatex.SetTextFont(root.gStyle.GetLabelFont())
      self.problatex.SetTextSize(self.pullHist.GetYaxis().GetLabelSize())
      self.problatex.SetTextAlign(12)
      yToDraw = 0.41 #bottom
      yToDraw = 0.92 #top
      #self.problatex.DrawLatex(0.18,yToDraw,"KS Prob: {0:.3g}".format(self.KSProb))
      self.problatex.DrawLatex(0.18,yToDraw,"#chi^{{2}}/NDF: {0:.3g}".format(self.normchi2))
      self.problatex.DrawLatex(0.18,yToDraw-0.08,"#chi^{{2}}  Prob: {0:.3g}".format(self.chi2Prob))

    pad2.Update()
    pad2.GetFrame().DrawClone()
    pad2.RedrawAxis() # Updates Axis Lines
  
    canvas.cd()
    self.tlatex.DrawLatex(0.33,0.96,PRELIMINARYSTRING)
    self.tlatex.DrawLatex(0.75,0.96,"#sqrt{{s}}={0}, L={1:.1f} fb^{{-1}}".format(energyStr,lumi))

  def getPullDistributionParams(self,pullList):
    pull = root.RooRealVar("pull","pull",-20,20)
    mean = root.RooRealVar("mean","pull Mean",0.0,-20,20)
    sigma = root.RooRealVar("sigma","pull sigma",1.0,0.01,20)
    self.pullGaus = root.RooGaussian("pullGaus","pullGaus",pull,mean,sigma)
    self.pullDS = root.RooDataSet("pullDS","pullDS",root.RooArgSet(pull))
    for i in pullList:
      pull.setVal(i)
      self.pullDS.add(root.RooArgSet(pull))
    self.pullFR = self.pullGaus.fitTo(self.pullDS,PRINTLEVEL)
    self.pullMean = mean
    self.pullSigma = sigma
    meanStr = "<Pull> = {0:.2f} #pm {1:.2f}".format(mean.getVal(), mean.getError())
    sigmaStr = "#sigma(Pull) = {0:.2f} #pm {1:.2f}".format(sigma.getVal(), sigma.getError())

    frame = pull.frame(root.RooFit.Bins(20))
    self.pullDS.plotOn(frame)
    self.pullGaus.plotOn(frame)
    frame.Draw()
    self.canvas.SaveAs("pullDist"+self.dataHist.GetName()+".png")
    return meanStr, sigmaStr

class CompareTwoHists:
  def __init__(self, hist1,hist2, canvas, xtitle, ytitle="Events",nDivX=7,nDivPullY=5,xlimits=[],ylimits=[],pullHistRangeY=[0.0,2.0],isPreliminary=True,is7TeV=False,lumi=5.0):
    nBinsX = hist1.GetNbinsX()
    assert(nBinsX == hist2.GetNbinsX())
    self.nBinsX = nBinsX
    self.hist1 = hist1
    self.hist2 = hist2
    self.canvas = canvas
    self.tlatex = root.TLatex()
    self.tlatex.SetNDC()
    self.tlatex.SetTextFont(root.gStyle.GetLabelFont())
    self.tlatex.SetTextSize(0.05)
    self.tlatex.SetTextAlign(22)

    if xlimits != []:
      self.hist1.GetXaxis().SetRangeUser(*xlimits)
      self.hist2.GetXaxis().SetRangeUser(*xlimits)
  
    # Make Pull Hist
    self.pullHist = hist1.Clone("pullHist"+hist1.GetName())
    self.pullHist.Reset()
    self.pullHist.SetLineColor(hist2.GetLineColor())
    self.pullErrorBand = root.TGraphAsymmErrors()
    self.pullErrorBand.SetFillColor(856)
    self.pullErrorBand.SetFillStyle(1001)
    self.pullErrorBand.SetLineStyle(2)
    self.pullErrorBand.SetLineColor(root.kBlack)
    for i in range(0,nBinsX+2):
      nhist1 = hist1.GetBinContent(i)
      nhist2 = hist2.GetBinContent(i)
      nhist1Err = hist1.GetBinError(i)
      nhist2Err = hist2.GetBinError(i)
      ratio = 0.0
      ratioErr = 0.0
      if nhist1 != 0.0 and nhist2 != 0.0:
        ratio = nhist2/nhist1
        ratioErr = nhist2/nhist1 * sqrt((nhist1Err/nhist1)**2+(nhist2Err/nhist2)**2)
      self.pullHist.SetBinContent(i,ratio)
      self.pullHist.SetBinError(i,ratioErr)
      tmpAxis = hist1.GetXaxis()
      self.pullErrorBand.SetPoint(i,tmpAxis.GetBinCenter(i),1.0)
      self.pullErrorBand.SetPointError(i,tmpAxis.GetBinLowEdge(i),tmpAxis.GetBinUpEdge(i),
                                                            nhist1Err/nhist1,nhist1Err/nhist1)
      #print("nData: %f, nMC: %f, error: %f, pull: %f" % (nData,nMC,error,pull))

    firstVizBin = self.pullHist.GetXaxis().GetFirst()
    lastVizBin = self.pullHist.GetXaxis().GetLast()
    for i in range(0,firstVizBin):
      self.pullErrorBand.SetPointEYhigh(i,self.pullErrorBand.GetErrorYhigh(firstVizBin))
      self.pullErrorBand.SetPointEYlow(i,self.pullErrorBand.GetErrorYlow(firstVizBin))
    for i in range(lastVizBin+1,nBinsX+2):
      self.pullErrorBand.SetPointEYhigh(i,self.pullErrorBand.GetErrorYhigh(lastVizBin))
      self.pullErrorBand.SetPointEYlow(i,self.pullErrorBand.GetErrorYlow(lastVizBin))

    #Find Maximum y-value
    max1 = hist1.GetMaximum()
    max2 = hist2.GetMaximum()
    max1Bin = hist1.GetMaximumBin()
    max2Bin = hist2.GetMaximumBin()
    max1 = hist1.GetBinContent(max1Bin)+hist1.GetBinError(max1Bin)
    max2 = hist2.GetBinContent(max2Bin)+hist2.GetBinError(max2Bin)
    ymax = 0.0
    if max1 > max2:
       ymax = max1
    else:
       ymax = max2
    self.ymax = ymax

    #Setup Canvas
    canvas.cd()
    canvas.Clear()
    pad1 = root.TPad("pad1"+hist1.GetName(),"",0.02,0.30,0.98,0.98,0)
    pad2 = root.TPad("pad2"+hist1.GetName(),"",0.02,0.01,0.98,0.29,0)
  
    pad1.SetBottomMargin(0.005);
    pad2.SetTopMargin   (0.005);
    pad2.SetBottomMargin(0.33);
  
    pad1.Draw() # Projections pad
    pad2.Draw() # Residuals   pad

    pad1Width = pad1.XtoPixel(pad1.GetX2())
    pad1Height = pad1.YtoPixel(pad1.GetY1())
    pad2Height = pad2.YtoPixel(pad2.GetY1())
    #pad1ToPad2FontScalingFactor = float(pad1Width)/pad2Height
    pad1ToPad2FontScalingFactor = float(pad1Height)/pad2Height
  
    # Main Pad
    pad1.cd();
    self.hist2.GetXaxis().SetTitle("")
    self.hist2.GetXaxis().SetLabelSize(0)
    self.hist2.GetYaxis().SetTitle(ytitle)
    self.hist2.GetYaxis().SetLabelSize(0.050)
    self.hist2.GetYaxis().SetTitleSize(0.055)
    self.hist2.GetXaxis().SetNdivisions(nDivX)
    if ylimits==[]:
      self.hist2.GetYaxis().SetRangeUser(0.0,ymax*1.04)
    else:
      self.hist2.GetYaxis().SetRangeUser(*ylimits)
    self.hist2.Draw("")
    self.hist1.Draw("same")
  
    # Pulls Pad
    pad2.cd()
    self.pullHist.SetTitle("")
    if xlimits != []:
      self.pullHist.GetXaxis().SetRangeUser(*xlimits)
    self.pullHist.GetXaxis().SetTitle(xtitle)
    self.pullHist.GetXaxis().CenterTitle(1)
    self.pullHist.GetXaxis().SetNdivisions(nDivX)
    self.pullHist.GetXaxis().SetTitleSize(0.055*pad1ToPad2FontScalingFactor)
    self.pullHist.GetXaxis().SetLabelSize(0.050*pad1ToPad2FontScalingFactor)
    self.pullHist.GetYaxis().SetTitle("Ratio")
    self.pullHist.GetYaxis().SetTitleSize(0.050*pad1ToPad2FontScalingFactor)
    self.pullHist.GetYaxis().SetLabelSize(0.040*pad1ToPad2FontScalingFactor)
    self.pullHist.GetYaxis().CenterTitle(1)
    self.pullHist.GetYaxis().SetTitleOffset(0.5)
    self.pullHist.GetYaxis().SetNdivisions(nDivPullY)
    self.pullHist.GetYaxis().SetRangeUser(*pullHistRangeY)
    self.pullHist.GetXaxis().SetTitleOffset(0.75*self.pullHist.GetXaxis().GetTitleOffset())
    self.pullHist.GetYaxis().SetTitleOffset(0.70)
    self.pullHist.SetFillColor(856)
    self.pullHist.SetFillStyle(1001)
    self.pullHist.Draw("")
    self.pullErrorBand.Draw("3")
    self.pullErrorBand.Draw("LX")
    #self.pullErrorBandLine = self.pullErrorBand.Clone(self.pullErrorBand.GetName()+"Line")
    #self.pullErrorBandLine.SetFillStyle(0)
    #self.pullErrorBandLine.Draw("same HIST L")
    self.pullHist.Draw("same")
    pad2.Update()
    pad2.GetFrame().DrawClone()
  
    canvas.cd()
    if isPreliminary:
      self.tlatex.DrawLatex(0.33,0.96,"CMS Preliminary")
    if is7TeV:
      self.tlatex.DrawLatex(0.75,0.96,"#sqrt{s}=8 TeV, L=%.2f fb^{-1}" % lumi)

class CompareTwoHistsAndData:
  def __init__(self, hist1,hist2, data, canvas, xtitle, ytitle="Events",nDivX=7,nDivPullY=5,xlimits=[],ylimits=[],pullHistRangeY=[0.0,2.0],isPreliminary=True,is7TeV=False,lumi=5.0,logy=False,integralPlot=False,energyStr="8TeV"):
    nBinsX = hist1.GetNbinsX()
    assert(nBinsX == hist2.GetNbinsX())
    assert(nBinsX == data.GetNbinsX())
    self.nBinsX = nBinsX
    self.hist1 = hist1
    self.hist2 = hist2
    self.data = data
    self.canvas = canvas
    self.tlatex = root.TLatex()
    self.tlatex.SetNDC()
    self.tlatex.SetTextFont(root.gStyle.GetLabelFont())
    self.tlatex.SetTextSize(0.05)
    self.tlatex.SetTextAlign(22)

    if xlimits != []:
      self.hist1.GetXaxis().SetRangeUser(*xlimits)
      self.hist2.GetXaxis().SetRangeUser(*xlimits)
  
    # Make Pull Hist
    self.pullHist1 = hist1.Clone("pullHist1"+data.GetName())
    self.pullHist1.Reset()
    self.pullHist2 = hist2.Clone("pullHist2"+data.GetName())
    self.pullHist2.Reset()
    for i in range(1,self.pullHist1.GetNbinsX()):
      nData = data.GetBinContent(i)
      nMC1 = hist1.GetBinContent(i)
      nMC2 = hist2.GetBinContent(i)
      error = data.GetBinError(i)
      pull1 = 0.0
      pull2 = 0.0
      if error != 0.0:
        pull1 = (nMC1 - nData)/error
        pull2 = (nMC2 - nData)/error
      self.pullHist1.SetBinContent(i,pull1)
      self.pullHist2.SetBinContent(i,pull2)

    #Find Maximum y-value
    max1 = hist1.GetMaximum()
    max2 = hist2.GetMaximum()
    max1Bin = hist1.GetMaximumBin()
    max2Bin = hist2.GetMaximumBin()
    max1 = hist1.GetBinContent(max1Bin)+hist1.GetBinError(max1Bin)
    max2 = hist2.GetBinContent(max2Bin)+hist2.GetBinError(max2Bin)
    ymax = 0.0
    if max1 > max2:
       ymax = max1
    else:
       ymax = max2
    self.ymax = ymax

    #Find min/max pulls
    max1 = self.pullHist1.GetMaximum()
    max2 = self.pullHist2.GetMaximum()
    pullmax = 0.0
    if max1 > max2:
       pullmax = max1
    else:
       pullmax = max2
    self.pullmax = pullmax
    min1 = self.pullHist1.GetMinimum()
    min2 = self.pullHist2.GetMinimum()
    pullmin = 0.0
    if min1 < min2:
       pullmin = min1
    else:
       pullmin = min2
    self.pullmin = pullmin

    #Setup Canvas
    canvas.cd()
    canvas.Clear()
    pad1 = root.TPad("pad1"+hist1.GetName(),"",0.02,0.30,0.98,0.98,0)
    pad2 = root.TPad("pad2"+hist1.GetName(),"",0.02,0.01,0.98,0.29,0)
  
    pad1.SetBottomMargin(0.005);
    pad2.SetTopMargin   (0.005);
    pad2.SetBottomMargin(0.33);
  
    pad1.Draw() # Projections pad
    pad2.Draw() # Residuals   pad

    pad1Width = pad1.XtoPixel(pad1.GetX2())
    pad1Height = pad1.YtoPixel(pad1.GetY1())
    pad2Height = pad2.YtoPixel(pad2.GetY1())
    #pad1ToPad2FontScalingFactor = float(pad1Width)/pad2Height
    pad1ToPad2FontScalingFactor = float(pad1Height)/pad2Height
  
    # Main Pad
    pad1.cd();
    self.hist2.SetTitle("")
    self.hist2.GetXaxis().SetTitle("")
    self.hist2.GetXaxis().SetLabelSize(0)
    self.hist2.GetYaxis().SetTitle(ytitle)
    self.hist2.GetYaxis().SetLabelSize(0.050)
    self.hist2.GetYaxis().SetTitleSize(0.055)
    self.hist2.GetXaxis().SetNdivisions(nDivX)
    if ylimits==[]:
      self.hist2.GetYaxis().SetRangeUser(0.0,ymax*1.04)
    else:
      self.hist2.GetYaxis().SetRangeUser(*ylimits)
    self.hist2.SetFillStyle(0)
    self.hist1.SetFillStyle(0)
    self.hist2.Draw("hist")
    self.hist1.Draw("hist same")
    self.data.Draw("pe same")
  
    # Pulls Pad
    pad2.cd()
    self.pullHist1.SetTitle("")
    if xlimits != []:
      self.pullHist1.GetXaxis().SetRangeUser(*xlimits)
    self.pullHist0 = self.pullHist1.Clone("pullHist0")
    self.pullHist0.Reset()
    self.pullHist0.SetLineColor(1)
    self.pullHist0.SetLineStyle(2)
    self.pullHist0.SetFillStyle(0)
    self.pullHist1.GetXaxis().SetTitle(xtitle)
    self.pullHist1.GetXaxis().CenterTitle(1)
    self.pullHist1.GetXaxis().SetNdivisions(nDivX)
    self.pullHist1.GetXaxis().SetTitleSize(0.055*pad1ToPad2FontScalingFactor)
    self.pullHist1.GetXaxis().SetLabelSize(0.050*pad1ToPad2FontScalingFactor)
    self.pullHist1.GetYaxis().SetTitle("#frac{MC-Data}{Error}")
    self.pullHist1.GetYaxis().SetTitleSize(0.050*pad1ToPad2FontScalingFactor)
    self.pullHist1.GetYaxis().SetLabelSize(0.040*pad1ToPad2FontScalingFactor)
    self.pullHist1.GetYaxis().CenterTitle(1)
    self.pullHist1.GetYaxis().SetTitleOffset(0.5)
    self.pullHist1.GetYaxis().SetNdivisions(nDivPullY)
    self.pullHist1.GetYaxis().SetRangeUser(pullmin*0.90,pullmax*1.1)
    self.pullHist1.GetXaxis().SetTitleOffset(0.75*self.pullHist1.GetXaxis().GetTitleOffset())
    #self.pullHist1.GetYaxis().SetTitleOffset(0.70)
    self.pullHist1.SetFillStyle(0)
    self.pullHist2.SetFillStyle(0)
    self.pullHist1.Draw("hist")
    self.pullHist0.Draw("hist same")
    self.pullHist1.Draw("hist same")
    self.pullHist2.Draw("hist same")
    pad2.Update()
    pad2.GetFrame().DrawClone()
  
    canvas.cd()
    self.tlatex.DrawLatex(0.33,0.96,PRELIMINARYSTRING)
    self.tlatex.DrawLatex(0.75,0.96,"#sqrt{{s}}={0}, L={1:.1f} fb^{{-1}}".format(energyStr,lumi))

def makeBootstrapHist(hist,outHist,entries=None):
 outHist.Reset()
 samples = entries
 if samples == None:
   integral = hist.Integral()
 for i in range(samples):
   outHist.Fill(hist.GetRandom())

def getMedianAndQuantileInterval(hist,amountForQuantile,doErrors=False):
    """ 
        Takes and input histogram, and an amount for the quantile 
        returns a list with: 
          [amountForQuantile, median, and 1.0-amountForQuantile] quantiles
    """
    quantilesToGet = array.array('d',[amountForQuantile,0.5,1.0-amountForQuantile])
    if doErrors:
      lowErrors = numpy.zeros(1000)
      medianErrors = numpy.zeros(1000)
      highErrors = numpy.zeros(1000)
      errors = []
      for i in range(1000):
        tmpHist = hist.Clone("tmpForQuantiles")
        makeBootstrapHist(hist,tmpHist,int(hist.GetEntries()))
        quantiles = array.array('d',[0.0,0.0,0.0])
        nQuantiles = tmpHist.GetQuantiles(3,quantiles,quantilesToGet)
        if(nQuantiles != 3):
          raise Exception("ROOT Hist Quantile Estimation didn't work!!")
        lowErrors[i] = quantiles[0]
        medianErrors[i] = quantiles[1]
        highErrors[i] = quantiles[2]
      quantiles = array.array('d',[0.0,0.0,0.0])
      nQuantiles = hist.GetQuantiles(3,quantiles,quantilesToGet)
      if(nQuantiles != 3):
          raise Exception("ROOT Hist Quantile Estimation didn't work!!")
      medianErros = []
      highErrors = []
      errors.append(numpy.std(lowErrors))
      errors.append(numpy.std(medianErrors))
      errors.append(numpy.std(highErrors))
      return list(quantiles), errors
    else:
      quantiles = array.array('d',[0.0,0.0,0.0])
      nQuantiles = hist.GetQuantiles(3,quantiles,quantilesToGet)
      if(nQuantiles != 3):
          raise Exception("ROOT Hist Quantile Estimation didn't work!!")
      return list(quantiles)

def sqrtThisHistogram(hist):
    """
        Sqrt's bin contents 
        of the input hist bin contents, properly treating the errors.
    """
    nBins = hist.GetNbinsX()

    for i in range(nBins+2):
      y = hist.GetBinContent(i)
      yErr = hist.GetBinError(i)
      if y < 0.0:
        print("Warning sqrtThisHIstogram: hist named %s bin %i has negative y value %f" % (hist.GetName(),i,y))
        hist.SetBinContent(i,0.0)
        hist.SetBinError(i,0.0)
        continue
      if y == 0.0:
        print("Warning sqrtThisHIstogram: hist named %s bin %i has zero y value" % (hist.GetName(),i))
        hist.SetBinContent(i,0.0)
        hist.SetBinError(i,0.0)
        continue
      hist.SetBinContent(i,sqrt(y))
      hist.SetBinError(i,yErr/(sqrt(2*y)))

def getSqrtCopyOfHistogram(hist):
    """
        Reterns a histogram of where the bin contents are the sqrt
        of the input hist bin contents, properly treating the errors.
    """
    outHist = hist.Clone(hist.GetName()+"SqrtHist")
    sqrtThisHistogram(outHist)
    return outHist

def drawSilly(isPreliminary=True,is7TeV=False):
    tlatex = root.TLatex()
    tlatex.SetNDC()
    tlatex.SetTextFont(root.gStyle.GetLabelFont())
    tlatex.SetTextSize(0.05)
    tlatex.SetTextAlign(22)
    if isPreliminary:
      tlatex.DrawLatex(0.33,0.96,"CMS Preliminary")
    if is7TeV:
      tlatex.DrawLatex(0.75,0.96,"#sqrt{s}=8 TeV, L=4.7 fb^{-1}")

def normalizeHist(hist):
  integral = hist.Integral(0,hist.GetNbinsX()+1)
  if integral != 0.0:
    hist.Scale(1.0/integral)

def showHistOverflow(hist):
  nBins = hist.GetNbinsX()

  overflow = hist.GetBinContent(nBins+1)
  overflowErr = hist.GetBinError(nBins+1)
  lastBin = hist.GetBinContent(nBins)
  lastBinErr = hist.GetBinError(nBins)

  hist.SetBinContent(nBins,lastBin+overflow)
  hist.SetBinError(nBins,sqrt(lastBinErr**2+overflowErr**2))

  underflow = hist.GetBinContent(0)
  underflowErr = hist.GetBinError(0)
  firstBin = hist.GetBinContent(1)
  firstBinErr = hist.GetBinError(1)

  hist.SetBinContent(1,firstBin+underflow)
  hist.SetBinError(1,sqrt(firstBinErr**2+underflowErr**2))

class PlotOfSlices:
  def __init__(self, hist2D, xtitle, ytitle, canvas, xlimits=[], ylimits=[],sliceLabelPrefix="",isPreliminary=True,is7TeV=False):
    canvas.cd(0)
    canvas.Clear()
    nBinsX = hist2D.GetNbinsX()
    nBinsY = hist2D.GetNbinsY()
    self.nBinsX = nBinsX
    self.nBinsY = nBinsY
    self.hist2D = hist2D
    self.canvas = canvas
    self.sliceLabelPrefix = sliceLabelPrefix
    self.tlatex = root.TLatex()
    self.tlatex.SetNDC()
    self.tlatex.SetTextFont(root.gStyle.GetLabelFont())
    self.tlatex.SetTextSize(0.05)
    self.tlatex.SetTextAlign(22)
    self.histList = []

    colorsListTmp = [root.kRed+1,root.kBlue+1,root.kGreen+1,root.kCyan,root.kMagenta+1]
    self.colorsList=[]
    for i in [0,-11,+2]:
        for j in range(len(colorsListTmp)):
            self.colorsList.append(colorsListTmp[j]+i)

    if xlimits != []:
      self.hist2D.GetXaxis().SetRangeUser(*xlimits)
    if ylimits != []:
      self.hist2D.GetYaxis().SetRangeUser(*ylimits)

    ymax = 0.0
    for i in range(nBinsX+2):
        tmpHist = root.TH1F(hist2D.GetName()+"_slice"+str(i),"",
                            nBinsY,hist2D.GetYaxis().GetXbins().GetArray())
        for j in range(nBinsY+2):
            tmpHist.SetBinContent(j,hist2D.GetBinContent(i,j))
        tmpMax = tmpHist.GetMaximum()
        if tmpMax > ymax:
            ymax = tmpMax
        tmpHist.SetLineColor(self.colorsList[i])
        self.histList.append(tmpHist)
    
    firstHist = self.histList[0]
    firstHist.SetTitle("")
    firstHist.GetXaxis().SetTitle(xtitle)
    firstHist.GetYaxis().SetTitle(ytitle)
    if xlimits != []:
        firstHist.GetXaxis().SetRangeUser(*xlimits)
    if ylimits==[]:
        firstHist.GetYaxis().SetRangeUser(0.0,ymax*1.05)
    else:
        firstHist.GetYaxis().SetRangeUser(*ylimits)

    firstHist.Draw("")
    for hist in self.histList[1:]:
        hist.Draw("same")

    if isPreliminary:
      self.tlatex.DrawLatex(0.33,0.96,"CMS Preliminary")
    if is7TeV:
      self.tlatex.DrawLatex(0.75,0.96,"#sqrt{s}=8 TeV, L=4.7 fb^{-1}")

    ## Lgend Part

    leg = root.TLegend(0.6,0.3,0.9,0.9)
    leg.SetLineColor(root.kWhite)
    leg.SetFillColor(root.kWhite)
    self.leg = leg
    xAxis = self.hist2D.GetXaxis()
    xBin = 0
    for hist in self.histList:
      tmpLabel = ""
      if xBin == 0:
        tmpLabel = "%s [0.0,%.1f]" % (sliceLabelPrefix,xAxis.GetBinUpEdge(xBin))
      elif xBin == nBinsX+1:
        tmpLabel = "%s [%.1f,#infty]" % (sliceLabelPrefix,xAxis.GetBinLowEdge(xBin))
      else:
        tmpLabel = "%s [%.1f,%.1f]" % (sliceLabelPrefix,xAxis.GetBinLowEdge(xBin),xAxis.GetBinUpEdge(xBin))
      leg.AddEntry(hist,tmpLabel,"l")
      xBin += 1
    leg.Draw("same")

def getIntegralHist(hist,setErrors=True):
  result = hist.Clone(hist.GetName()+"_Integral")
  nBins = result.GetNbinsX()
  for i in range(nBins+1):
    sumw = 0.0
    sumw2 = 0.0
    for j in range(i,nBins+2):
      sumw += result.GetBinContent(j)
      sumw2 += (result.GetBinError(j))**2
    result.SetBinContent(i,sumw)
    if setErrors:
        result.SetBinError(i,sumw2**0.5)
  return result

def hist2to1(hist):
  assert(hist.InheritsFrom("TH1"))
  result = None
  nBinsX = hist.GetNbinsX()
  nBinsY = hist.GetNbinsY()
  totalBins = (nBinsX+2)*(nBinsY+2) - 2 #include underflow/overflow
  if hist.InheritsFrom("TH2F"):
    result = root.TH1F(hist.GetName()+"_1d","",totalBins,0,totalBins)
  elif hist.InheritsFrom("TH2D"):
    result = root.TH1D(hist.GetName()+"_1d","",totalBins,0,totalBins)
  else:
    print("Error: hist2to1: Input hist must be TH2F or TH2D, exiting.")
    sys.exit(1)
  k = 0
  for i in range(nBinsX+2):
    for j in range(nBinsY+2):
      tmp = hist.GetBinContent(i,j)
      tmpErr = hist.GetBinError(i,j)
      result.SetBinContent(k,tmp)
      result.SetBinError(k,tmpErr)
      k += 1
  return result

def hist2to1CollapseY(hist,xcuts=[]):
  assert(hist.InheritsFrom("TH1"))
  result = None
  nBinsX = hist.GetNbinsX()
  nBinsY = hist.GetNbinsY()
  ymin = hist.GetYaxis().GetXmin()
  ymax = hist.GetYaxis().GetXmax()
  totalBins = (nBinsX+2)*(nBinsY+2) - 2 #include underflow/overflow
  if hist.InheritsFrom("TH2F"):
    result = root.TH1F(hist.GetName()+"_1d","",nBinsY,ymin,ymax)
  elif hist.InheritsFrom("TH2D"):
    result = root.TH1D(hist.GetName()+"_1d","",nBinsY,ymin,ymax)
  else:
    print("Error: hist2to1CollapseY: Input hist must be TH2F or TH2D, exiting.")
    sys.exit(1)
  minBinX = 0
  maxBinX = nBinsX+2
  if len(xcuts)==2:
    minBinX = hist.GetXaxis().FindBin(xcuts[0])
    maxBinX = hist.GetXaxis().FindBin(xcuts[1])
    if hist.GetXaxis().GetBinCenter(maxBinX)> xcuts[1]:
        maxBinX -= 1
  for j in range(nBinsY+2):
    tmpSum = 0.0
    tmpSumErr2 = 0.0
    for i in range(minBinX,maxBinX):
      tmp = hist.GetBinContent(i,j)
      tmpErr = hist.GetBinError(i,j)
      tmpSum += tmp
      tmpSumErr2 += tmpErr*tmpErr
    result.SetBinContent(j,tmpSum)
    result.SetBinError(j,sqrt(tmpSumErr2))
  return result

def shrinkTH1(hist,xlow,xhigh,deleteOld=False):
  assert(hist.InheritsFrom("TH1"))
  taxis=hist.GetXaxis()
  oldXlow=taxis.GetXmin()
  oldXhigh=taxis.GetXmax()
  assert(xlow >= oldXlow)
  assert(xhigh <= oldXhigh)
  lowBin = taxis.FindBin(xlow)
  highBin = taxis.FindBin(xhigh)
  if taxis.GetBinLowEdge(highBin)==float(xhigh):
    highBin -= 1
  xlow = taxis.GetBinLowEdge(lowBin)
  xhigh = taxis.GetBinUpEdge(highBin)
  oldN = hist.GetNbinsX()
  newN = int((xhigh-xlow)/(oldXhigh-oldXlow)*oldN)
  name = hist.GetName()
  title = hist.GetTitle()
  hist.SetName(name+"_Old")
  newHist = root.TH1F(name,title,newN,xlow,xhigh)
  newHist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
  newHist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())
  for iOld,iNew in zip(range(lowBin,highBin+1),range(1,newN+1)):
    newHist.SetBinContent(iNew,hist.GetBinContent(iOld))
    newHist.SetBinError(iNew,hist.GetBinError(iOld))
  if deleteOld:
    hist.Delete()
  return newHist

def linearChi2(xList,yList,order,yErrList=None,funcName="poly"):
  assert(len(xList)==len(yList))
  xList = numpy.array(xList)
  yList = numpy.array(yList)

  poly = None
  stats = None
  weights = None
  if yErrList == None:
    weights = 1.0/numpy.sqrt(yList)
  else:
    assert(len(yErrList)==len(yList))
    yErrList = numpy.array(yErrList)
    weights = 1.0/yErrList
  if funcName == "poly":
    poly,stats = numpy.polynomial.polyfit(xList,yList,order,full=True,w=weights)
  else:
    poly,stats = numpy.polynomial.chebfit(xList,yList,order,full=True,w=weights)

  # For Debug
  fig = mpl.figure()
  ax = fig.add_subplot(111)
  ax.errorbar(xList,yList,yerr=1.0/weights,linestyle="None",color="k")

  polyInst = None

  if funcName == "poly":
    polyInst = numpy.polynomial.Polynomial(poly)
  else:
    polyInst = numpy.polynomial.Chebyshev(poly)

  yy = polyInst(xList)
  ax.plot(xList,yy,"-b")
  
  fig.savefig("debugLinearChi2.png")

  return poly

def linearChi2TH1(hist,order,funcName="poly"):
  nBinsX = hist.GetNbinsX()
  x = numpy.zeros(nBinsX)
  y = numpy.zeros(nBinsX)
  err = numpy.zeros(nBinsX)
  for i in range(1,nBinsX+1):
    x[i-1] = hist.GetXaxis().GetBinCenter(i)
    y[i-1] = hist.GetBinContent(i)
    err[i-1] = hist.GetBinError(i)
  print x
  print y
  result = linearChi2(x,y,order,yErrList=err,funcName=funcName)
  print result
  return result

def toyHistogram(hist):
  nBins = hist.GetNbinsX()
  random = root.TRandom3()
  for i in range(nBins+2):
    mean = hist.GetBinContent(i)
    n = random.Poisson(mean)
    err = sqrt(n)
    hist.SetBinContent(i,n)
    hist.SetBinError(i,err)

def getXbinsHighLow(hist,low,high):
  axis = hist.GetXaxis()
  xbinLow = axis.FindBin(low)
  xbinHigh = axis.FindBin(high)
  #print("xbinhigh: {0}, {1}, {2}".format(xbinHigh,axis.GetBinLowEdge(xbinHigh),float(high)))
  if axis.GetBinLowEdge(xbinHigh)==float(high):
    xbinHigh -= 1
  return xbinLow, xbinHigh

def getIntegralAll(hist,boundaries=[]):
  xbinLow = None
  xbinHigh = None
  if len(boundaries)==0:
    xbinLow = 0
    xbinHigh = hist.GetXaxis().GetNbins()
  elif len(boundaries)==2:
    xbinLow, xbinHigh = getXbinsHighLow(hist,boundaries[0],boundaries[1])
  else:
    return -1
  if hist.InheritsFrom("TH2"):
    nBinsY = hist.GetYaxis().GetNbins()
    return hist.Integral(xbinLow,xbinHigh,0,nBinsY+1)
  elif hist.InheritsFrom("TH1"):
    return hist.Integral(xbinLow,xbinHigh)
  else:
    return -1

def getIntegralLowHigh(hist,lowBoundaries,highBoundaries):
  lowInt = getIntegralAll(hist,lowBoundaries)
  highInt = getIntegralAll(hist,highBoundaries)
  return lowInt+highInt

def sqrtTH1(hist):
  nBins = hist.GetNbinsX()
  for i in range(nBins+2):
    n = hist.GetBinContent(i)
    nErr = hist.GetBinError(i)
    if n < 0.0:
      n = 0.0
    hist.SetBinContent(i,sqrt(n))
    hist.SetBinError(i,sqrt(nErr))

class CrossSecsErrs:
  def __init__(self,csvDict):
    self.data = csvDict
    self.err = {}
    self.errUp = {}
    self.errDown = {}
    self.lnN = {}
    for key in self.data:
      self.errUp[key] = self.data[key][1]/100.
      self.errDown[key] = self.data[key][2]/100.
      self.err[key] = max(abs(self.data[key][1]),abs(self.data[key][2]))/100.
      self.lnN[key] = self.err[key] + 1.0
  def __getitem__(self,key):
    return self.data[key][0]

def readCSVXS(filename):
  f = open(filename)
  rd = csv.reader(f)
  result = {}
  for row in rd:
    if len(row) == 0:
        continue
    if len(row[0]) == 0:
        continue
    if re.search(r"[^\d.\s]",row[0]):
        continue
    mass = float(row[0])
    prec = "0"
    if mass % 1 > 0:
        prec = '1'
    result[("{0:."+prec+"f}").format(mass)] = [float(i) for i in row[1:]]
  f.close()
  return CrossSecsErrs(result)

def getRooBinningFromTH1(hist):
  nbins = hist.GetNbinsX()
  xmax = hist.GetXaxis().GetXmax()
  xmin = hist.GetXaxis().GetXmin()
  print nbins,xmax,xmin
  return root.RooFit.RooBinning(nbins,xmin,xmax)

def getBinningFromTH1(hist,newName):
  nbins = hist.GetNbinsX()
  xmax = hist.GetXaxis().GetXmax()
  xmin = hist.GetXaxis().GetXmin()
  print nbins,xmax,xmin
  return newName,newName,nbins,xmin,xmax

def getRooVarRange(variable,name):
  assert(variable.InheritsFrom("RooRealVar"))
  assert(type(name)==str)
  binning = variable.getBinning(name)
  return binning.lowBound(), binning.highBound()

def saveAs(canvas,name):
  canvas.SaveAs(name+".png")
  canvas.SaveAs(name+".pdf")
  canvas.SaveAs(name+".eps")
  canvas.SaveAs(name+".root")

def setLegPos(leg,legPos):
  leg.SetX1NDC(legPos[0])
  leg.SetX2NDC(legPos[2])
  leg.SetY1NDC(legPos[1])
  leg.SetY2NDC(legPos[3])

def getBinWidthStr(hist):
    binWidth = (hist.GetXaxis().GetXmax()-hist.GetXaxis().GetXmin())/hist.GetXaxis().GetNbins()
    binWidthPrec = "0"
    if binWidth % 1 > 0.0:
      binWidthPrec = "1"
      if binWidth*10 % 1 > 0.0:
        binWidthPrec = "2"
    return ("{0:."+binWidthPrec+"f}").format(binWidth)

class EfficiencyReader:
  def __init__(self,fileDir="effDir/"):
    self.data = {}
    self.fileDir = fileDir
    for ifn in glob.glob(fileDir+"*.txt"):
      fmatch = re.match(r".*/Eff_(.+)Higgs([0-9.]+).txt",ifn)
      if not fmatch:
        print("Warning: EfficiencyReader: filename: {0} isn't recognized".format(ifn))
        continue
      prodMode = fmatch.group(1)
      mass = fmatch.group(2)
      if not self.data.has_key(prodMode):
        self.data[prodMode] = {}
      f = open(ifn)
      for iline in f:
        lmatch = re.match(r"([\w]+)[\s]+([\d.]+)[\s]+([\d.]+)",iline)
        if not fmatch:
          print("Warning: EfficiencyReader: text line isn't recognized: \n{0}\n in file: {1}".format(iline,ifn))
          continue
        category = lmatch.group(1)
        efficiency = float(lmatch.group(2))
        efficiencyError = float(lmatch.group(3))
        if not self.data[prodMode].has_key(category):
          self.data[prodMode][category] = {}
        if not self.data[prodMode][category].has_key(mass):
          self.data[prodMode][category][mass] = {}
        self.data[prodMode][category][mass]['eff'] = efficiency
        self.data[prodMode][category][mass]['effErr'] = efficiencyError
        
  def __getitem__(self,key):
    return self.data[key]
  def __call__(self,prodMode,category,mass):
    eff = self.data[prodMode][category][mass]['eff']
    err = self.data[prodMode][category][mass]['effErr']
    return eff, err
  def getEfficiency(self,prodMode,category,mass):
    return self.data[prodMode][category][mass]['eff']
  def getEfficiencyError(self,prodMode,category,mass):
    return self.data[prodMode][category][mass]['effErr']
  def __str__(self):
    result = ""
    for mode in self.data:
      result += "{0}:\n".format(mode)
      sortedCats = sorted(self.data[mode].keys())
      for cat in sortedCats:
        result += "  {0}:\n".format(cat)
        for mass in self.data[mode][cat]:
          eff = self.data[mode][cat][mass]['eff']
          err = self.data[mode][cat][mass]['effErr']
          result += "    {0:5}:  {1:8.2%}  +/-  {2:8.2%}\n".format(mass,eff,err)
    return result
  def __repr__(self):
    return str(self)

if __name__ == "__main__":

  print("Running helpers.py")
  eff = EfficiencyReader()
  print eff
  
