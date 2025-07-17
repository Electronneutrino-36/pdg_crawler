import numpy
import json
import argparse

# test if the pdg package is installed
try:
    import pdg
    print("Module pdg found!")
except ModuleNotFoundError:
    print("Module pdg not found!")
    print("Please install it using: python -m pip install pdg")
    exit()

# for nice visualization of the loading bar
try: 
    from alive_progress import alive_bar; import time, logging
    print("Module alive-progress found!")
except ModuleNotFoundError:
    print("Module not found!")
    print("Please install it using: python3 -m pip install alive-progress")
    exit()


# main function to get meson data
def update_mesons(api):
    print("Retrieving meson data.")
    part_dict = {}                                                  # define temporary dictionary to store the data
    with alive_bar(len(list(api.get_particles()))) as bar:          # initialize the loading bar
        for item in api.get_particles():                            # loop over the particles
            particle_data = api.get('{}'.format(item.pdgid))        # get the particles by PDG-ID
            for i in range(0,len(particle_data)):                   # loop over the retrieved data

                # the next few lines are to construct the quantum numbers
                if ( particle_data[i].quantum_C != None and particle_data[i].quantum_G != None ):
                    qn_string = '{}^{}({}^{}{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_G,particle_data[i].quantum_J,particle_data[i].quantum_P,particle_data[i].quantum_C)
                elif ( particle_data[i].quantum_C != None and particle_data[i].quantum_G == None ):
                    qn_string = '{}({}^{}{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_J,particle_data[i].quantum_P,particle_data[i].quantum_C)
                elif ( particle_data[i].quantum_C == None and particle_data[i].quantum_G != None ):
                    qn_string = '{}^{}({}^{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_G,particle_data[i].quantum_J,particle_data[i].quantum_P)
                else:
                    qn_string = '{}({}^{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_J,particle_data[i].quantum_P)


                # define the parameters of interest
                mass = 0
                mass_error_pos = 0
                mass_error_neg = 0
                width = 0
                width_error_pos = 0
                width_error_neg = 0

                if particle_data[i].is_meson == True:                               # only get the data for the mesons

                    try:                                                            # try if there are values in the PDG database
                        try:                                                        # try if the mass and width values come with asymmetric errors
                            for jmasses in particle_data[i].masses():
                                mass = jmasses.value
                                mass_error_pos = jmasses.error_positive
                                mass_error_neg = jmasses.error_negative
                            for jwidths in particle_data[i].widths():
                                width = jwidths.value
                                width_error_pos = jwidths.error_positive
                                width_error_neg = jwidths.error_negative
                        except:
                            mass = particle_data[i].mass
                            mass_error_pos = particle_data[i].mass_error
                            mass_error_neg = particle_data[i].mass_error
                            width = particle_data[i].width
                            width_error_pos = particle_data[i].width_error
                            width_error_neg = particle_data[i].width_error


                        # write the data to the dictionary
                        part_dict['{}'.format(particle_data[i].name)] = {"QN": qn_string,
                                                                         "Mass": mass, 
                                                                        "Mass Error positive": mass_error_pos, 
                                                                        "Mass Error negative": mass_error_neg, 
                                                                        "Width": width,
                                                                        "Width Error positive": width_error_pos,
                                                                        "Width Error negative": width_error_neg,
                                                                        "Charge": particle_data[i].charge}
                    except:
                        print("No mass properties found at the time for the {}!".format(particle_data[i].name))
                        continue
                else:
                    continue
                
            time.sleep(0.01)                                                        # update timer for the loading bar
            bar()                                                                   # display loading bar
    
    return part_dict

# main function to get baryon data
def update_baryons(api):
    print("Retrieving baryon data.")
    part_dict = {}
    with alive_bar(len(list(api.get_particles()))) as bar:
        for item in api.get_particles():
            particle_data = api.get('{}'.format(item.pdgid))
            for i in range(0,len(particle_data)):
                if ( particle_data[i].quantum_C != None and particle_data[i].quantum_G != None ):
                    qn_string = '{}^{}({}^{}{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_G,particle_data[i].quantum_J,particle_data[i].quantum_P,particle_data[i].quantum_C)
                elif ( particle_data[i].quantum_C != None and particle_data[i].quantum_G == None ):
                    qn_string = '{}({}^{}{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_J,particle_data[i].quantum_P,particle_data[i].quantum_C)
                elif ( particle_data[i].quantum_C == None and particle_data[i].quantum_G != None ):
                    qn_string = '{}^{}({}^{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_G,particle_data[i].quantum_J,particle_data[i].quantum_P)
                else:
                    qn_string = '{}({}^{})'.format(particle_data[i].quantum_I,particle_data[i].quantum_J,particle_data[i].quantum_P)

                mass = 0
                mass_error_pos = 0
                mass_error_neg = 0
                width = 0
                width_error_pos = 0
                width_error_neg = 0
                if particle_data[i].is_baryon == True:
                    try:
                        try:
                            for jmasses in particle_data[i].masses():
                                mass = jmasses.value
                                mass_error_pos = jmasses.error_positive
                                mass_error_neg = jmasses.error_negative
                            for jwidths in particle_data[i].widths():
                                width = jwidths.value
                                width_error_pos = jwidths.error_positive
                                width_error_neg = jwidths.error_negative
                        except:
                            mass = particle_data[i].mass
                            mass_error_pos = particle_data[i].mass_error
                            mass_error_neg = particle_data[i].mass_error
                            width = particle_data[i].width
                            width_error_pos = particle_data[i].width_error
                            width_error_neg = particle_data[i].width_error
                        part_dict['{}'.format(particle_data[i].name)] = {"QN": qn_string,
                                                                         "Mass": mass, 
                                                                        "Mass Error positive": mass_error_pos, 
                                                                        "Mass Error negative": mass_error_neg, 
                                                                        "Width": width,
                                                                        "Width Error positive": width_error_pos,
                                                                        "Width Error negative": width_error_neg,
                                                                        "Charge": particle_data[i].charge}
                    except:
                        print("No mass properties found at the time for the {}!".format(particle_data[i].name))
                        continue
                else:
                    continue
                
            time.sleep(0.01)
            bar()
    return part_dict

# get meson and baryon data at the same time
def update_particles(api):
    mesons_updated = update_mesons(api)
    baryons_updated = update_baryons(api)
    return mesons_updated, baryons_updated

# write data as .txt or .dat file
def write_to_file(data,internal_filename):
    savefile = open(internal_filename,"w")
    savefile.write(f"{'Name':<24} | {'I^(G)(J^P(C))':^18} | {'M  [MeV]':>10} | {'dM+ [MeV]':>10} | {'dM- [MeV]':>10} | {'W [MeV]':>10} | {'dW+ [MeV]':>10} | {'dW- [MeV]':>10} | {'C':<10}\n")

    for msns in data.keys():
        if ( data[msns]['Width'] != None and data[msns]['Mass Error positive'] != None ):
            savefile.write("{:<24}   {:^18}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
                                                                        data[msns]['Mass Error positive'],data[msns]['Mass Error negative'],
                                                                        data[msns]['Width'],data[msns]['Width Error positive'],data[msns]['Width Error negative'],
                                                                        data[msns]['Charge']))
        elif ( data[msns]['Width'] == None  and data[msns]['Mass Error positive'] != None ):
            savefile.write("{:<24}   {:^18}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10}  {:>10}  {:>10}  {:>10}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
                                                                        data[msns]['Mass Error positive'],data[msns]['Mass Error negative'],
                                                                        "-", "-", "-",
                                                                        data[msns]['Charge']))
        elif ( data[msns]['Width'] != None  and data[msns]['Mass Error positive'] == None ):
            savefile.write("{:<24}   {:^18}  {:>10.3f}  {:>10}  {:>10}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
                                                                        "-","-",
                                                                        data[msns]['Width'],data[msns]['Width Error positive'],data[msns]['Width Error negative'],
                                                                        data[msns]['Charge']))
        else:
            savefile.write("{:<24}   {:^18}  {:>10.3f}  {:>10}  {:>10}  {:>10}  {:>10}  {:>10}  {:>10}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
                                                                        "-", "-",
                                                                        "-", "-", "-",
                                                                        data[msns]['Charge']))
    savefile.close()

# start of program 

