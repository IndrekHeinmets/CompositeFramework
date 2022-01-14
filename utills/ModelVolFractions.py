# Volume values from the abaqus models

# Plain:
total_vol = 5637.79
matrix_vol = 3628.08

# Basket:
total_vol = 5740.60
matrix_vol = 3761.03

# Mock-Leno:
total_vol = 5680.39
matrix_vol = 3683.53

def find_volume_fraction(total_vol, matrix_vol):
    fiber_vol = total_vol - matrix_vol
    vf_fibres = round(fiber_vol / total_vol, 4)
    vf_matrix = round(matrix_vol / total_vol, 4)
    return vf_fibres, vf_matrix

VolFraction_Fibres, VolFraction_Matrix = find_volume_fraction(total_vol, matrix_vol)
print(f"Volume Fraction of CF Fibers: {VolFraction_Fibres * 100}%")
print(f"Volume Fraction of Resin Matrix: {VolFraction_Matrix * 100}%")