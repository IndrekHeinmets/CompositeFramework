# Volume values from the Abaqus models (total_vol, matrix_vol)
volumes = {'Plain': (5637.79, 3628.08),
           'Basket': (5740.60, 3761.03),
           'Mock-Leno': (5680.39, 3683.53),
           'Satin': (5760.88, 3784.17),
           'Twill': (5785.66, 3794.70),
           'Extra': (5850.77, 3859.38),
           'MsRVE': (1728003.13, 1124817.00)}


def find_volume_fraction(volumes, model):
    total_vol, matrix_vol = volumes[model]
    fiber_vol = total_vol - matrix_vol
    vf_fibres = round(fiber_vol / total_vol, 4)
    vf_matrix = round(matrix_vol / total_vol, 4)
    return vf_fibres, vf_matrix


# Enter the name of the model (Plain, Basket, Mock-Leno, Satin, Twill, Extra, MsRVE):
model = 'Mock-Leno'

VolFraction_Fibres, VolFraction_Matrix = find_volume_fraction(volumes, model)
print(f"Volume Fraction of CF Fibers: {VolFraction_Fibres * 100}%")
print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix * 100}%")
