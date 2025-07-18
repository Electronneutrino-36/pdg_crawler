# PDG Data crawler

## Prerequisits
To use the following data crawler, one needs to have two python packages installed:
- pdg
- alive-progress

These can be installed via:

``
python3 -m pip install pdg
python3 -m pip install alive-progress
``

## Usage
To use, simply call the python program "update_pdg_data.py" via


`` 
python3 update_pdg_data.py 
``

Per default it calls the PDG API and pulls the properties of all the mesons **and** baryons from the PDG and 
writes it into the .json files: "mesons.json" and "baryons.json"

## Changing the filetype
If one does not want to get a .json file as an output, one can add the command line argument

``
python3 update_pdg_data.py -filetype .desired_filetype
``

where desired_filetype can be anything: .txt, .dat, etc....


## Changing the name of the output files
One can change the name of the meson files by adding the command line argument:

``
python3 update_pdg_data.py -mfilename new_meson_filename
``

Equally for the baryon, one adds the command line argument:

``
python3 update_pdg_data.py -bfilename new_baryon_filename
``

## Choosing only the mesons or baryons
If one wants to only update the data for the mesons **or** the baryons, one can use the command line argument:

``
python3 update_pdg_data.py -meson
``

for only the meson data and 

``
python3 update_pdg_data.py -baryon
``

for the baryon data.
