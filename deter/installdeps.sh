#!/bin/sh

here=$(pwd)
tardir=$(dirname $0)
cd ${tardir}
tardir=$(pwd)
mkdir -p ${tardir}/work

for deb in "libev3" "libev-dev"; do
    echo "looking for ${deb}"
    file=$(find ${tardir} -name "*${deb}*")
    dpkg -i ${tardir}/${file}
done


for mod in "argparse" "pyev"; do
    file=$(ls ${tardir} | grep ${mod})
    tar -C ${tardir}/work -xzvf ${tardir}/${file}
    builddir=$(find ${tardir}/work -name "*${mod}*")
    cd ${builddir}
    python ./setup.py install
    cd ${tardir}
done

tar -C ${tardir}/work -xzvf ${tardir}/rscadstreamer-1.0.tar.gz
cd ${tardir}/work/rscadstreamer-1.0
python ./setup.py install
cd ${tardir}

rm -rf ${tardir}/work
cd ${here}
