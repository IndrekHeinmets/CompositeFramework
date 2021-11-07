from math import sqrt
import sympy as sym

# y = sin 0.5x
# L = integral(sqrt(1 + (dy/dx)^2))

x, y = sym.symbols('x y')
x_beg, x_end = 0, 10
curve_len = 0
exp = sym.sin(0.5 * x)
print(exp)

curve_len = sym.integrate(sqrt(1 + sym.diff(exp, x)^2), (x, x_beg, x_end))
print(curve_len)



# # INTEGRATION
# # Indefinite integration of cos(x) w.r.t. dx
# integral1 = sym.integrate(sym.cos(x), x)
# print('indefinite integral of cos(x): ',
#       integral1)
#
# # definite integration of cos(x) w.r.t. dx between -1 to 1
# integral2 = sym.integrate(sym.cos(x), (x, -1, 1))
# print('definite integral of cos(x) between -1 to 1: ',
#       integral2)
#
# # definite integration of exp(-x) w.r.t. dx between 0 to ∞
# integral3 = sym.integrate(sym.exp(-x), (x, 0, sym.oo))
# print('definite integral of exp(-x) between 0 to ∞: ',
#       integral3)
#
# # DIFFERENTIATION
# # expression of which we have to find derivative
# exp = x ** 3 * y + y ** 3 + z
#
# # Differentiating exp with respect to x
# derivative1_x = sym.diff(exp, x)
# print('derivative w.r.t x: ',
#       derivative1_x)
#
# # Differentiating exp with respect to y
# derivative1_y = sym.diff(exp, y)
# print('derivative w.r.t y: ',
#       derivative1_y)
