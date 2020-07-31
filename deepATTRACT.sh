# User must provide pocket points in a single pdb file (pocket.pdb).
# For instance:
# Use POCASA [http://g6altair.sci.hokudai.ac.jp/g6/service/pocasa/]
# with parameters probe 2A, spacing grid 1A ;
# select all pockets (protein_TopN_pockets.pdb) ;
# merge all relevant pockets into pocket.pdb

receptor=protein.pdb        #
pocket=pocket.pdb           # can be from POCASA
n=500                       # recommanded 500
x=7                         # recommanded 7 for 3-pyrmidines, 10 for 3-purines
motif=AAA                   # RNA 3nt motif to be docked
np=36                       # nb CPU
t1=100                      # score threshold for filtering
t2=10000000                 # nb starting positions to select for docking
t3=1000000                  # top-ranked docking solutions to refine
t4=100000                   # top-ranked refined solutions to assembly
name=points-${x}A-n$n
parals="--np $np --jobsize 100000"

#dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
#export PYTHONPATH=$PYTHONPATH:$dir/scripts
ligandr=`head -n 1 ${motif}r.list`
Nconf=`cat ${motif}r.list|wc -l`
gridparams=" --grid 1 gridheader"

set -u -e

if false;then
    echo '**************************************************************'
    echo 'Create starting positions in pocket'
    echo '**************************************************************'
    if [ ! -s pocket.dat ];then

        #convert protein into coarse-grained representation
        python2 $ATTRACTTOOLS/reduce.py $receptor receptorr.pdb > /dev/null

        #select starting points with enough space around
        $dir/scripts/find_neighbored_points.py $pocket $x $n > $name
        $dir/scripts/select-lines.py $pocket $name > $name.pdb

        #convert into translation-rotation vectors
        $dir/scripts/pdb2translate.py $name.pdb  receptorr.pdb > translate.dat
        # rotations to apply to each conformer
        cat $ATTRACTDIR/../rotation.dat > rotation.dat
        $ATTRACTDIR/systsearch > pocket.dat
        #for visualisation
        sed 's/POSI PRO/  CA PRO/' translate.dat > translate.pdb
    fi

    echo '**************************************************************'
    echo ' cluster conformers at 3A '
    echo '**************************************************************'

    if [ ! -s ${motif}r-clust3.0 ];then
        # Cluster library by RMSD at 3A cutoff
        $dir/scripts/fastcluster_npy.py ${motif}r.npy 3
        awk '{print $4}' ${motif}r-clust3.0 > 3A.list
        $dir/scripts/select-lines.py ${motif}r.list 3A.list > ${motif}r-clust3.0.list
    fi
    Nconf3A=`cat ${motif}r-clust3.0|wc -l`

    #distribute conformers (3A clustering) to each starting position
    if [ ! -s filter1.dat ];then
    pypy $ATTRACTTOOLS/ensemblize.py pocket.dat $Nconf3A 2 all > pocket-ens-$Nconf3A.dat
    fi
    start=pocket-ens-$Nconf3A.dat

fi

if false;then
    echo '**************************************************************'
    echo 'Create starting positions in pocket'
    echo '**************************************************************'
    if [ ! -s pocket.dat ];then

        #convert protein into coarse-grained representation
        python2 $ATTRACTTOOLS/reduce.py $receptor receptorr.pdb > /dev/null

        #select starting points with enough space around
        $dir/scripts/find_neighbored_points.py $pocket $x $n > $name
        $dir/scripts/select-lines.py $pocket $name > $name.pdb

        #convert into translation-rotation vectors
        $dir/scripts/pdb2translate.py $name.pdb  receptorr.pdb > translate.dat
        # rotations to apply to each conformer
        cat $ATTRACTDIR/../rotation.dat > rotation.dat
        $ATTRACTDIR/systsearch > pocket.dat
        #for visualisation
        sed 's/POSI PRO/  CA PRO/' translate.dat > translate.pdb
    fi
fi

if false;then
    echo '**************************************************************'
    echo ' cluster conformers at 3A '
    echo '**************************************************************'

    if [ ! -s ${motif}r-clust3.0 ];then
        # Cluster library by RMSD at 3A cutoff
        $dir/scripts/fastcluster_npy.py ${motif}r.npy 3
        awk '{print $4}' ${motif}r-clust3.0 > 3A.list
        $dir/scripts/select-lines.py ${motif}r.list 3A.list > ${motif}r-clust3.0.list
    fi
    Nconf3A=`cat ${motif}r-clust3.0|wc -l`

    #distribute conformers (3A clustering) to each starting position
    if [ ! -s filter1.dat ];then
    pypy $ATTRACTTOOLS/ensemblize.py pocket.dat $Nconf3A 2 all > pocket-ens-$Nconf3A.dat
    fi
    start=pocket-ens-$Nconf3A.dat
fi

if false;then
    echo '**************************************************************'
    echo 'calculate receptorgrid grid'
    echo '**************************************************************'
    #$ATTRACTDIR/shm-clean
    awk '{print substr($0,58,2)}' $ligandr | sort -nu > alphabet
    $ATTRACTDIR/make-grid-omp receptorr.pdb $ATTRACTDIR/../attract.par 5.0 7.0 gridheader  --shm --alphabet alphabet
    gridparams=" --grid 1 gridheader"

fi
scoreparams="$ATTRACTDIR/../attract.par receptorr.pdb $ligandr --score --fix-receptor $parals $gridparams --rcut 50"

if false;then
    echo '**************************************************************'
    echo ' filter 1: score conformers clustered at 3A '
    echo '**************************************************************'

    if [ ! -s filter1.dat ];then
    python2 $ATTRACTDIR/../protocols/attract.py $start $scoreparams --ens 2 ${motif}r-clust3.0.list --output clust3A.score
    python2 $ATTRACTTOOLS/fill-energies.py $start clust3A.score > /dev/shm/clust3A-scored.dat

    # select poses with score < $t1
    python2 $ATTRACTTOOLS/filter-energy.py /dev/shm/clust3A-scored.dat $t1 > clust3A-filter1.dat

    # Distribute to each position 1A-conformers in the clusters of the well-scored 3A-conformers
    $dir/scripts/ensemblize_custom.py clust3A-filter1.dat --clust ${motif}r-clust3.0 > filter1.dat
fi

echo '**************************************************************'
echo ' filter 2: score conformers clustered at 1A '
echo '**************************************************************'
python2 $ATTRACTDIR/../protocols/attract.py filter1.dat $scoreparams --ens 2 ${motif}r.list --output filter1.score
python2 $ATTRACTTOOLS/fill-energies.py filter1.dat filter1.score > filter1-scored.dat
$dir/scripts/select-dat.py filter1-scored.dat --rank $t2 >  filter2.dat
rm filter1.score filter1.dat

fi

echo '**************************************************************'
echo ' dock from external starting positions '
echo '**************************************************************'

if false;then
    ### add starting points all around the surface (for non-concave binding regions)

    # Translations to apply after each rotation of each conformer, to place it at each starting point
    # The distance from the protein surface depend on the size of the ligand.
    # Rather than computing it for each 3-nt, it is computed with the largest 3-nt
    $ATTRACTDIR/translate receptorr.pdb GGG-largestrc.pdb > translate.dat
    # combine rotations and translations
    $ATTRACTDIR/systsearch > systsearch.dat

    $dir/scripts/ensemblize_custom.py systsearch.dat --nconf $Nconf --max 10000000 --output external > external.list

fi

dockparams="$ATTRACTDIR/../attract.par receptorr.pdb $ligandr --fix-receptor $gridparams $parals --rcut 50 --vmax 100"

cat /dev/null > top1percent.list
for external in `cat external.list`; do
    if [ ! -s $external-top1percent.dat ];then
        if [ ! -s $external-min.dat ] ;then
            python2 $ATTRACTDIR/../protocols/attract.py $external.dat $dockparams --ens 2 ${motif}r.list --output $external-min.dat
        fi
        rm $external.dat
        python2 $ATTRACTDIR/../protocols/attract.py $external-min.dat $scoreparams --ens 2 ${motif}r.list --output $external-min.score
        $dir/scripts/select-dat.py $external-min-scored.dat --percent 1 --inpscores $external-min.score --energies > $external-top1percent.dat
        echo $external-top1percent.dat >> top1percent.list
    fi
done

$dir/scripts/concat_dat.py `cat top1percent.list` > external-top1percent.dat
$ATTRACTDIR/deredundant external-top1percent.dat 2 --ens 0 $Nconf --radgyr 9 > external-top1percent-dr.dat


echo '**************************************************************'
echo ' filter 3: dock conformers clustered at 1A '
echo '**************************************************************'

dockparams="$ATTRACTDIR/../attract.par receptorr.pdb $ligandr --fix-receptor $gridparams $parals --rcut 50 --vmax 100"

python2 $ATTRACTDIR/../protocols/attract.py filter2.dat $dockparams --ens 2 ${motif}r.list --output filter2-min.dat
python2 $ATTRACTDIR/../protocols/attract.py filter2-min.dat $scoreparams --ens 2 ${motif}r.list --output filter2-min.score
python2 $ATTRACTTOOLS/fill-energies.py filter2-min.dat filter2-min.score > filter2-min-scored.dat
$dir/scripts/select-dat.py filter2-min-scored.dat --rank $t3 > filter3.dat

echo '**************************************************************'
echo ' filter 4: refine docked poses '
echo '**************************************************************'

refineparams="$ATTRACTDIR/../attract.par receptorr.pdb $ligandr --fix-receptor $parals --rcut 50 --vmax 100"
python2 $ATTRACTDIR/../protocols/attract.py filter3.dat $refineparams --ens 2 ${motif}r.list --output filter3-refined.dat
# sort poses by score, remove redundant poses, then select top-scored
python2 $ATTRACTTOOLS/sort.py filter3-refined.dat > filter3-refined-sorted.dat
$ATTRACTDIR/deredundant filter3-refined-sorted.dat 2 --ens 0 $Nconf > filter3-refined-sorted-dr.dat
$ATTRACTTOOLS/top filter3-refined-sorted-dr.dat $t4 > filter4.dat

echo '**************************************************************'
echo ' Evaluate docking results (for test-cases) '
echo '**************************************************************'
#Compute ligand-RMSD for each fragment
for i in `seq 12 -1 1`; do
    python2 $ATTRACTDIR/lrmsd.py filter4.dat $ligandr boundfrag/frag$i\r.pdb --ens 2 ${motif}r.list --allatoms |awk '{print NR, $2}' > frag$i.lrmsd
done

#$ATTRACTDIR/shm-clean
