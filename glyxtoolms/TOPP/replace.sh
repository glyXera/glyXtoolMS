pythonpath="/afs/mpi-magdeburg.mpg.de/data/bpt/personnel_folders/MarkusPioch/software/Envs/glyxtoolms/bin/python"
openmspath="/afs/mpi-magdeburg.mpg.de/data/bpt/personnel_folders/MarkusPioch/software/OpenMS"

### ----------------- resolve possible sysmlinks --------------------###

openmspathUnlinked=`readlink -f "$openmspath"`

# check if openmspath is set to a real path
if [ ! -d "$openmspathUnlinked" ]
then
  echo "OpenMS path '$openmspathUnlinked' is not an existing directory!"
  exit 3
fi

### -------------- create script and external paths -----------------###
scriptpath=$openmspathUnlinked/share/OpenMS/SCRIPTS
externalpath=$openmspathUnlinked/share/OpenMS/TOOLS/EXTERNAL

### ------------------------- pythonpath ----------------------------###

# check if pythonpath is set correctly to the python executable
if [ ! -f "$pythonpath" ]
then
  echo "Python executable could not be found at '$pythonpath'"
  exit 3
fi

### ------------------------- scriptpath ----------------------------###

# check if scriptpath is set correctly to share/OPENMS/SCRIPTS
if [[ ! "$scriptpath" =~ ^.+share/OpenMS/SCRIPTS$ ]]
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
if [[ ! "$externalpath" =~ ^.+share/OpenMS/TOOLS/EXTERNAL$ ]]
then
    echo "Externalpath does not seem to point to share/OpenMS/TOOLS/EXTERNAL!"
    exit 3
fi

# check if externalpath is set to a real path
if [ ! -d "$externalpath" ]
then
  echo "EXTERNAL folder path '$externalpath' is not an existing directory!"
  exit 3
fi

### ------------------------- copy files ----------------------------###

for fullfile in *.ttd
do
    echo "Processing $fullfile file..";
    filename=$(basename "$fullfile")
    sed -e "s|{pythonpath}|$pythonpath|" -e "s|{scriptpath}|$scriptpath|"  "$fullfile" > "$externalpath/$filename"
done

for fullfile in *.py
do
    echo "Processing $fullfile file..";
    filename=$(basename "$fullfile")
    cat  "$fullfile" > "$scriptpath/$filename"
    
done
