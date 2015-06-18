pythonpath="/afs/mpi-magdeburg.mpg.de/data/bpt/personnel_folders/MarkusPioch/software/Envs/glyxbox/bin/python"
scriptpath="/afs/mpi-magdeburg.mpg.de/data/bpt/personnel_folders/MarkusPioch/software/OpenMS/share/OpenMS/SCRIPTS/"
externalpath="/afs/mpi-magdeburg.mpg.de/home/pioch/Data/Projekte/GlyxBox/GlyxSuite/TOPP/EXTERNAL/"

### ----------------- resolve possible sysmlinks --------------------###
scriptpathUnlinked=`readlink -f "$scriptpath"`
externalpathUnlinked=`readlink -f "$externalpath"`

#sed -e "s|{pythonpath}|$pythonpath|" -e "s|{scriptpath}|$scriptpath|"  test.ttd > output.ttd

### ------------------------- pythonpath ----------------------------###

# check if pythonpath is set correctly to the python executable
if [ ! -f "$pythonpath" ]
then
  echo "Python executable could not be found at '$pythonpath'"
  exit 3
fi

### ------------------------- scriptpath ----------------------------###

# check if scriptpath is set correctly to share/OPENMS/SCRIPTS
if [[ ! "$scriptpathUnlinked" =~ ^.+share/OpenMS/SCRIPTS$ ]]
then
    echo "Scriptpath does not seem to point to share/OpenMS/SCRIPTS/!"
    exit 3
fi

# check if scriptpath is set to a real path
if [ ! -d "$scriptpath" ]
then
  echo "Scriptpath '$scriptpath' is not an existing directory!"
  exit 3
fi

### ------------------------ externalpath ---------------------------###

# check if externalpath is set correctly to share/OPENMS/SCRIPTS
if [[ ! "$externalpathUnlinked" =~ ^.+share/OpenMS/TOOLS/EXTERNAL$ ]]
then
    echo "Scriptpath does not seem to point to share/OpenMS/TOOLS/EXTERNAL!"
    exit 3
fi

# check if externalpath is set to a real path
if [ ! -d "$externalpath" ]
then
  echo "EXTERNAL folfer path '$externalpath' is not an existing directory!"
  exit 3
fi


for fullfile in *.ttd
do
    echo "Processing $fullfile file..";
    filename=$(basename "$fullfile")
    sed -e "s|{pythonpath}|$pythonpath|" -e "s|{scriptpath}|$scriptpath|"  "$fullfile" > "$externalpathUnlinked/$filename"
done


