import numpy as np
import json
import argparse

# test if the pdg package is installed
try:
    import pdg
    print("Module pdg found!")
except ModuleNotFoundError:
    print("Module pdg not found!")
    print("Please install it using: python3 -m pip install pdg")
    exit()

# for nice visualization of the loading bar
try: 
    from alive_progress import alive_bar; import time, logging
    print("Module alive-progress found!")
except ModuleNotFoundError:
    print("Module not found!")
    print("Please install it using: python3 -m pip install alive-progress")
    exit()

def disentangle_mass_width(val_str):
    f_b_o = val_str.find("(")              # first bracket open
    f_b_c = val_str.find(")")              # first bracket close
    mass_values = val_str[f_b_o+1:f_b_c]

    i_s = ["-i(", "- i (", "-i (", "- i("]
    for i in i_s:
        if val_str.find(i) != -1:
            s_b_o = val_str.find(i)
            ifin = i
            break

    # s_b_o = val_str.find("-i(")
    width_values = val_str[s_b_o+len(ifin):-1]

    return mass_values, width_values

def disentangle_value_range(val_str):
    delims = ["TO", "to", "--"]
    for idel in delims:
        if val_str.find(idel) != -1:
            delim = idel
            break

    two_delim_flag = False

    f_del = val_str.find(delim)
    # check to see if there is a second delimiter
    d_loc = [i for i in range(len(val_str)) if val_str.startswith(delim, i)]                        # location of the delimiters

    if len(d_loc) != 1:
        two_delim_flag = True

    if two_delim_flag == False:
        val_1 = int(val_str[:f_del])
        val_2 = int(val_str[f_del+len(delim):])
    else:
        val_1 = int(val_str[:d_loc[0]])
        val_2 = int(val_str[d_loc[1]+len(delim):])

    av = np.mean([val_1,val_2])
    std = np.std([val_1,val_2])

    return av, std
    

def get_av_plus_std(meas):
    delim = "--"
    find_del = meas.find(delim)
    val_1 = int(meas[:find_del])
    val_2 = int(meas[find_del+len("--"):])

    av = np.mean([val_1,val_2])
    std = np.std([val_1,val_2])

    return av, std


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

                    try:
                        testmass = particle_data[i].mass
                    except:
                        mass = None
                        mass_error_pos = None
                        mass_error_neg = None
                    else:
                        if ( particle_data[i].mass is None or particle_data[i].mass_error is None ):
                            for ims in particle_data[i].masses():

                                if ( ims.value is not None and ims.error_positive is not None and ims.error_negative is not None):
                                    mass = ims.value
                                    mass_error_pos = ims.error_positive
                                    mass_error_neg = ims.error_negative
                                elif ims.value_text.find("~") != -1:
                                    mass = ims.value
                                    mass_error_pos = None
                                    mass_error_neg = None
                                elif ims.value_text.find("i") != -1 :
                                    mass_i = disentangle_mass_width(ims.value_text)[0]
                                    mass, m_err = disentangle_value_range(mass_i)
                                    mass_error_pos = m_err
                                    mass_error_neg = m_err
                                else:
                                    mass, m_err = disentangle_value_range(ims.value_text)
                                    mass_error_pos = m_err
                                    mass_error_neg = m_err
                        else:
                            mass = particle_data[i].mass
                            mass_error_pos = particle_data[i].mass_error
                            mass_error_neg = particle_data[i].mass_error
                    

                    try:
                        testwidth = particle_data[i].width
                    except:
                        width = None
                        width_error_pos = None
                        width_error_neg = None
                    else:
                        if ( particle_data[i].width is None or particle_data[i].width_error is None ) :
                            for iws in particle_data[i].widths():

                                if ( iws.value is not None and iws.error_positive is not None and iws.error_negative is not None):
                                    width = iws.value
                                    width_error_pos = iws.error_positive
                                    width_error_neg = iws.error_negative
                                elif iws.value_text.find("~") != -1:
                                    width = iws.value
                                    width_error_pos = None
                                    width_error_neg = None
                                elif iws.value_text.find("i") != -1:
                                    width_i = disentangle_mass_width(iws.value_text)[1]
                                    width, w_err = disentangle_value_range(width_i)
                                    width_error_pos = w_err
                                    width_error_neg = w_err
                                else:
                                    width, w_err = disentangle_value_range(iws.value_text)
                                    width_error_pos = w_err
                                    width_error_neg = w_err
                        else:
                            width = particle_data[i].width
                            width_error_pos = particle_data[i].width_error
                            width_error_neg = particle_data[i].width_error
                    
                    
                    if mass != None:
                        if mass > 100.0 :
                            mass = mass/1000
                            if mass_error_pos != None:
                                mass_error_pos = mass_error_pos/1000
                                mass_error_neg = mass_error_neg/1000

                    if width != None:
                        if width > 5:
                            width = width/1000
                            if width_error_pos != None:
                                width_error_pos = width_error_pos/1000
                                width_error_neg = width_error_neg/1000

                    
                    # print(particle_data[i].name,"  m = ",mass, " dm+ = ", mass_error_pos, " dm- = ", mass_error_neg, 
                    #       " w = ", width, " dw+ = ", width_error_pos, " dw- = ", width_error_neg)
                    
                    

                    # write the data to the dictionary
                    part_dict['{}'.format(particle_data[i].name)] = {"QN": qn_string,
                                                                        "Mass": mass, 
                                                                    "Mass Error positive": mass_error_pos, 
                                                                    "Mass Error negative": mass_error_neg, 
                                                                    "Width": width,
                                                                    "Width Error positive": width_error_pos,
                                                                    "Width Error negative": width_error_neg,
                                                                    "Charge": particle_data[i].charge}
                    
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
                        testmass = particle_data[i].mass
                    except:
                        mass = None
                        mass_error_pos = None
                        mass_error_neg = None
                    else:
                        if ( particle_data[i].mass is None or particle_data[i].mass_error is None ):
                            for ims in particle_data[i].masses():

                                if ( ims.value is not None and ims.error_positive is not None and ims.error_negative is not None):
                                    mass = ims.value
                                    mass_error_pos = ims.error_positive
                                    mass_error_neg = ims.error_negative
                                elif ims.value_text.find("~") != -1:
                                    mass = ims.value
                                    mass_error_pos = None
                                    mass_error_neg = None
                                elif ims.value_text.find("i") != -1 :
                                    mass_i = disentangle_mass_width(ims.value_text)[0]
                                    mass, m_err = disentangle_value_range(mass_i)
                                    mass_error_pos = m_err
                                    mass_error_neg = m_err
                                else:
                                    mass, m_err = disentangle_value_range(ims.value_text)
                                    mass_error_pos = m_err
                                    mass_error_neg = m_err
                        else:
                            mass = particle_data[i].mass
                            mass_error_pos = particle_data[i].mass_error
                            mass_error_neg = particle_data[i].mass_error
                    

                    try:
                        testwidth = particle_data[i].width
                    except:
                        width = None
                        width_error_pos = None
                        width_error_neg = None
                    else:
                        if ( particle_data[i].width is None or particle_data[i].width_error is None ) :
                            for iws in particle_data[i].widths():

                                if ( iws.value is not None and iws.error_positive is not None and iws.error_negative is not None):
                                    width = iws.value
                                    width_error_pos = iws.error_positive
                                    width_error_neg = iws.error_negative
                                elif iws.value_text.find("~") != -1:
                                    width = iws.value
                                    width_error_pos = None
                                    width_error_neg = None
                                elif iws.value_text.find("i") != -1:
                                    width_i = disentangle_mass_width(iws.value_text)[1]
                                    width, w_err = disentangle_value_range(width_i)
                                    width_error_pos = w_err
                                    width_error_neg = w_err
                                else:
                                    width, w_err = disentangle_value_range(iws.value_text)
                                    width_error_pos = w_err
                                    width_error_neg = w_err
                        else:
                            width = particle_data[i].width
                            width_error_pos = particle_data[i].width_error
                            width_error_neg = particle_data[i].width_error
                    
                    
                    if mass != None:
                        if mass > 100.0 :
                            mass = mass/1000
                            if mass_error_pos != None:
                                mass_error_pos = mass_error_pos/1000
                                mass_error_neg = mass_error_neg/1000

                    if width != None:
                        if width > 5:
                            width = width/1000
                            if width_error_pos != None:
                                width_error_pos = width_error_pos/1000
                                width_error_neg = width_error_neg/1000

                    
                    # print(particle_data[i].name,"  m = ",mass, " dm+ = ", mass_error_pos, " dm- = ", mass_error_neg, 
                    #       " w = ", width, " dw+ = ", width_error_pos, " dw- = ", width_error_neg)
                    
                    # write the data to the dictionary
                    part_dict['{}'.format(particle_data[i].name)] = {"QN": qn_string,
                                                                        "Mass": mass, 
                                                                    "Mass Error positive": mass_error_pos, 
                                                                    "Mass Error negative": mass_error_neg, 
                                                                    "Width": width,
                                                                    "Width Error positive": width_error_pos,
                                                                    "Width Error negative": width_error_neg,
                                                                    "Charge": particle_data[i].charge}
                    

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
    savefile.write(f"{'Name':<24} | {'I^(G)(J^P(C))':^18} | {'M  [GeV]':>10} | {'dM+ [GeV]':>10} | {'dM- [GeV]':>10} | {'W [GeV]':>10} | {'dW+ [GeV]':>10} | {'dW- [GeV]':>10} | {'C':<10}\n")

    for msns in data.keys():
        # print("{}   {}  {}  {}  {}  {}  {}  {}  {}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
        #                                                                 data[msns]['Mass Error positive'],data[msns]['Mass Error negative'],
        #                                                                 data[msns]['Width'],data[msns]['Width Error positive'],data[msns]['Width Error negative'],
        #                                                                 data[msns]['Charge']))
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
        elif ( data[msns]['Width'] != None  and data[msns]['Mass'] != None and data[msns]['Mass Error positive'] == None ):
            savefile.write("{:<24}   {:^18}  {:>10.3f}  {:>10}  {:>10}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10}\n".format(msns,data[msns]['QN'],data[msns]['Mass'],
                                                                        "-","-",
                                                                        data[msns]['Width'],data[msns]['Width Error positive'],data[msns]['Width Error negative'],
                                                                        data[msns]['Charge']))
        elif ( data[msns]['Width'] != None  and data[msns]['Mass'] == None and data[msns]['Mass Error positive'] == None ):
            savefile.write("{:<24}   {:^18}  {:>10}  {:>10}  {:>10}  {:>10.3f}  {:>10.3f}  {:>10.3f}  {:>10}\n".format(msns,data[msns]['QN'],"-",
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

