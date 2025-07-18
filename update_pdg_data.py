import argparse
import numpy as np

from pdg_crawler import *                                           # load the pdg crawler functions

parser = argparse.ArgumentParser()
parser.add_argument("-meson", "--meson_properties", action='store_true', help="Toggle on to update the meson properties.")
parser.add_argument("-baryon", "--baryon_properties", action='store_true', help="Toggle on to update the baryon properties.")
parser.add_argument("-mfilename", "--meson_filename", type=str, default='mesons', help="Filename to store the meson data.")
parser.add_argument("-bfilename", "--baryon_filename", type=str, default='baryons', help="Filename to store the baryon data.")
parser.add_argument("-filetype", "--type_for_file", type=str, default='.json', help="Choose type of file for the stored data. Default is .json")
args = parser.parse_args()

pdg_api = pdg.connect(pedantic=False)
print("Initialized PDG API")

# Uncomment to show all the particles

# for item in pdg_api.get_particles():
#     print(item.pdgid,"  ", item.description)


# define the meson and baryon dictionaries
mesons = {}
baryons = {}
# write meson and baryon data to dictionaries
if ( args.meson_properties == True and args.baryon_properties == False ):
    mesons = update_mesons(pdg_api)
elif ( args.meson_properties == False and args.baryon_properties == True ):
    baryons = update_baryons(pdg_api)
else:
    mesons, baryons = update_particles(pdg_api)

name_of_meson_file = args.meson_filename+args.type_for_file
name_of_baryon_file = args.baryon_filename+args.type_for_file

if len(mesons) != 0:
    print("Writing meson data to file: " + name_of_meson_file)
if len(baryons) != 0:
    print("Writing baryon data to file: " + name_of_baryon_file)

# write data as .json file
if args.type_for_file == '.json':
    if len(mesons) != 0:
        with open(name_of_meson_file, 'w') as f:
            json.dump(mesons,f,ensure_ascii=False)
    if len(baryons) != 0:
        with open(name_of_baryon_file, 'w') as f:
            json.dump(baryons,f,ensure_ascii=False)

# write data to .dat file
else:
    if len(mesons) != 0:
        write_to_file(mesons,name_of_meson_file)
    if len(baryons) != 0:
        write_to_file(baryons,name_of_baryon_file)

