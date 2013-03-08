#!/bin/bash
echo "Sourcing cmsset_default.sh"
cd /afs/cern.ch/cms/sw
source cmsset_default.sh
export SCRAM_ARCH=slc5_amd64_gcc462
echo "SCRAM_ARCH is $SCRAM_ARCH"
cd $LS_SUBCWD
echo "In Directory: "
pwd
eval `scramv1 runtime -sh`
echo "cmsenv success!"
date

TXTSUFFIX=".txt"
FILENAME=$1
DIRNAME="Dir"$1"Dir"
ROOTFILENAME=${1%$TXTSUFFIX}.root

mkdir $DIRNAME
cp $FILENAME $DIRNAME/
cp $ROOTFILENAME $DIRNAME/
cd $DIRNAME

echo "executing combine -M Asymptotic $FILENAME >& $FILENAME.out"

combine -M Asymptotic $FILENAME >& $FILENAME.out

echo "executing combine -M ProfileLikelihood -d $FILENAME --signif --usePLC >& $FILENAME.sig"

combine -M ProfileLikelihood -d $FILENAME --signif --usePLC >& $FILENAME.sig
rm -f roostats*
rm -f higgsCombineTest*.root

echo "executing combine -M ProfileLikelihood -d $FILENAME --signif --expectSignal=1 -t -1 --toysFreq >& $FILENAME.expsig"

combine -M ProfileLikelihood -d $FILENAME --signif --expectSignal=1 -t -1 >& $FILENAME.expsig
##combine -M ProfileLikelihood -d $FILENAME --signif --expectSignal=1 -t -1 --toysFreq >& $FILENAME.expsig
rm -f roostats*
rm -f higgsCombineTest*.root

echo "executing combine -M MaxLikelihoodFit --rMax 50 --plots --saveNormalizations $FILENAME >& $FILENAME.mu"

combine -M MaxLikelihoodFit --rMax 50 --plots --saveNormalizations $FILENAME >& $FILENAME.mu
rm -f roostats*
rm -f higgsCombineTest*.root

combine -M ChannelCompatibilityCheck --saveFitResult --rMax 50 $FILENAME >> logCCC
mv higgsCombineTest.ChannelCompatibilityCheck.*.root ../$FILENAME.CCC.root

rm -f roostats*
rm -f higgsCombineTest*.root
cp $FILENAME.out ..
cp $FILENAME.mu ..
cp $FILENAME.sig ..
cp mlfit.root ../$FILENAME.root
for subname in *_fit_s.png; do
  cp $subname ../${FILENAME%$TXTSUFFIX}_$subname
done
#cp $FILENAME.expsig ..

echo "done"
date

