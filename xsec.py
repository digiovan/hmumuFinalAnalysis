import ROOT as root

LUMI=9.833

#scaleHiggsBy = 50.0 #See in Z'
#scaleHiggsBy = 25.0 #See in Boosted Z
#scaleHiggsBy = 15.0
#scaleHiggsBy = 5.0 #See in VBF
scaleHiggsBy = 1.0
#scaleHiggsBy = 50.0

xsec = {}
xsec["vbfHmumu125"] = 3.338e-4 * scaleHiggsBy
xsec["vbfHmumu150"] = 3.338e-4 * scaleHiggsBy
xsec["ggHmumu125"] = 4.236e-3 * scaleHiggsBy
xsec["ggHmumu"] = xsec["ggHmumu125"]
xsec["ZHmumu"] = 8.556e-5 * scaleHiggsBy
xsec["WHmumu"] = 1.512e-4 * scaleHiggsBy

xsec["DYJetsToLL"] = 3503.71   ## madgraph
xsec["ttbar"] = 225.197   ## madgraph

nEventsMap = {}
nEventsMap["vbfHmumu125"] = 9990
nEventsMap["vbfHmumu150"] = 10000
nEventsMap["ggHmumu125"] = 9998
nEventsMap["ggHmumu"] = nEventsMap["ggHmumu125"]
nEventsMap["ZHmumu"] = 10000
nEventsMap["WHmumu"] = 10000
#nEventsMap["DYJetsToLL"] = 36277961 # GPs Ntuples w/o my changes
#nEventsMap["DYJetsToLL"] = 30361028 # GPs Ntuples w/ my changes CMSSW_5_2_X
nEventsMap["DYJetsToLL"] = 30459503 # GPs Ntuples w/ my changes CMSSW_5_3_X
nEventsMap["ttbar"] = 6416135 # GPs Ntuples w/ my changes CMSSW_5_3_X

backgroundList = [
"DYJetsToLL",
"ttbar"
]

signalList = [
"vbfHmumu125",
"ggHmumu125"
]

dataList = [
"SingleMuRun2012Av1",
"SingleMuRun2012Bv1",
"SingleMuRun2012Cv1",
"SingleMuRun2012Cv2"

#"DoubleMuRun2012Av1",
#"DoubleMuRun2012Bv1",
#"DoubleMuRun2012Cv1",
#"DoubleMuRun2012Cv2"
]

legendEntries = {}
legendEntries["DYJetsToLL"] = "Z+Jets"
legendEntries["ttbar"] = "t#bar{t}"
legendEntries["vbfHmumu125"] = "VBF H->#mu#mu"
legendEntries["vbfHmumu150"] = "VBF H->#mu#mu m_{H}=150 GeV"
legendEntries["ggHmumu"] = "ggH->#mu#mu"
legendEntries["ggHmumu125"] = "ggH->#mu#mu"
legendEntries["ZHmumu"] = "ZH, H->#mu#mu"
legendEntries["WHmumu"] = "WH, H->#mu#mu"
legendEntries["ttbar"] = "t#bar{t}"

colors = {}
colors["DYJetsToLL"] = root.kOrange
colors["ttbar"] = root.kGreen+3
colors["vbfHmumu150"] = root.kBlue
colors["vbfHmumu125"] = root.kBlue
colors["ggHmumu"] = root.kRed
colors["ggHmumu125"] = root.kRed
colors["ZHmumu"] = root.kGreen+1
colors["WHmumu"] = root.kGreen+1
colors["ttbar"] = root.kGreen-1

##################################################
