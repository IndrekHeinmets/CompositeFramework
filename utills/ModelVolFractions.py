# Volume values from the Abaqus models:
#   RVE's -> (total_vol, matrix_vol, fiber_vol)
#   Composites's -> (total_vol, matrix_vol)
volumes = {'RVE1': (1728005.38, 931469.31, 603186.25),
           'RVE2': (1728008.25, 931308.44, 603186.06),
           'RVE3': (1728005.75, 930292.94, 603185.63),
           'Plain': (5637.79, 3628.08),
           'Basket': (5740.60, 3761.03),
           'Mock-Leno': (5680.39, 3683.53),
           'Satin': (5760.88, 3784.17),
           'Twill': (5785.66, 3794.70),
           'Extra': (5850.77, 3859.38), }


def find_volume_fraction_microstructure(volumes, model):
    total_vol, matrix_vol, fiber_vol = volumes[model]
    interphase_vol = total_vol - (matrix_vol + fiber_vol)
    vf_fibers = round(fiber_vol / total_vol, 4)
    vf_matrix = round(matrix_vol / total_vol, 4)
    vf_interphase = round(interphase_vol / total_vol, 4)
    return vf_fibers, vf_matrix, vf_interphase


def find_volume_fraction_mesostructure(volumes, model):
    total_vol, matrix_vol = volumes[model]
    fiber_vol = total_vol - matrix_vol
    vf_fibers = round(fiber_vol / total_vol, 4)
    vf_matrix = round(matrix_vol / total_vol, 4)
    return vf_fibers, vf_matrix


if __name__ == '__main__':
    # Enter the name of the model (RVE1, RVE2, RVE3, Plain, Basket, Mock-Leno, Satin, Twill, Extra):
    model = 'RVE1'

    if model == 'RVE1' or model == 'RVE2' or model == 'RVE3':
        VolFraction_Fibers, VolFraction_Matrix, VolFraction_Interphase = find_volume_fraction_microstructure(volumes, model)
        print(f"Volume Fraction of CF Fibers: {VolFraction_Fibers}")
        print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix}")
        print(f"Volume Fraction of Interphase Medium: {VolFraction_Interphase}")
    else:
        VolFraction_Fibers, VolFraction_Matrix = find_volume_fraction_mesostructure(volumes, model)
        print(f"Volume Fraction of CF Fibers: {VolFraction_Fibers}")
        print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix}")
