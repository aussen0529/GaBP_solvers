import sympy as sp
import numpy as np
from scipy.sparse import coo_matrix
import bvp

def construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y):
    rhs = sp.simplify(a*exact.diff(x, 2) + b*exact.diff(y, 2) + alpha*exact.diff(x, 1) + beta*exact.diff(y, 1)+ q*(exact.diff(x, 1)).diff(y, 1))
    f_rhs = sp.lambdify((x, y), rhs, modules='math')
    a = sp.lambdify((x, y), a, modules='math')
    b = sp.lambdify((x, y), b, modules='math')
    alpha = sp.lambdify((x, y), alpha, modules='math')
    beta = sp.lambdify((x, y), beta, modules='math')
    q = sp.lambdify((x, y), q, modules='math')
    up = exact.subs(y, L_y)
    left = exact.subs(x, 0)
    down = exact.subs(y, 0)
    right = exact.subs(x, L_x)
    up = sp.lambdify(x, up, modules='math')
    left = sp.lambdify(y, left, modules='math')
    down = sp.lambdify(x, down, modules='math')
    right = sp.lambdify(y, right, modules='math')
    exact = sp.lambdify((x, y), exact, modules='numpy')
    return a, alpha, b, beta, q, f_rhs, up, left, down, right, exact

def construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y):
    rhs = sp.simplify(a*exact.diff(x, 2) + b*exact.diff(y, 2) + alpha*exact.diff(x, 1) + beta*exact.diff(y, 1))
    f_rhs = sp.lambdify((x, y), rhs, modules='math')
    a = sp.lambdify((x, y), a, modules='math')
    b = sp.lambdify((x, y), b, modules='math')
    alpha = sp.lambdify((x, y), alpha, modules='math')
    beta = sp.lambdify((x, y), beta, modules='math')
    up = sp.simplify((exact.diff(y, 1)).subs(y, L_y))
    left = sp.simplify((exact.diff(x, 1)).subs(x, 0))
    down = sp.simplify((exact.diff(y, 1)).subs(y, 0))
    right = sp.simplify((exact.diff(x, 1)).subs(x, L_x))
    up = sp.lambdify(x, up, modules='math')
    left = sp.lambdify(y, left, modules='math')
    down = sp.lambdify(x, down, modules='math')
    right = sp.lambdify(y, right, modules='math')
    exact = sp.lambdify((x, y), exact, modules='numpy')
    return a, alpha, b, beta, f_rhs, up, left, down, right, exact

def construct_matrix(equation, type, L_x, L_y, n_x, n_y):

    if type == 'Dirichlet':
        h_x = L_x/(n_x+1); h_y = L_y/(n_y+1)
        a, alpha, b, beta, q, f_rhs, up, left, down, right, exact = equation(L_x, L_y)
        x, y = np.linspace(h_x, L_x-h_x, n_x), np.linspace(h_y, L_y-h_y, n_y)
        X, Y = np.meshgrid(x, y, indexing='ij')
        f = (exact(X, Y)).reshape(-1,)

        row, col, values = bvp.d2A(a, alpha, b, beta, q, L_x, L_y, n_x, n_y)
        rhs = bvp.mod_rhs(a, alpha, b, beta, q, f_rhs, up, left, down, right, L_x, L_y, n_x, n_y)

        A = coo_matrix((values, (row, col))).tocsc()

    if type == 'Neumann':
        a, alpha, b, beta, f_rhs, up, left, down, right, exact = equation(L_x, L_y)
        x, y = np.linspace(0, L_x, n_x+2), np.linspace(0, L_y, n_y+2)
        X, Y = np.meshgrid(x, y, indexing='ij')
        f = exact(X, Y)
        f[0, 0] = f[-1, -1] = f[-1, 0] = f[0, -1] = 1
        f = f.reshape(-1,)

        row, col, values = bvp.d2A_Neumann(a, alpha, b, beta, L_x, L_y, n_x, n_y)
        rhs = bvp.mod_rhs_Neumann(f_rhs, up, left, down, right, L_x, L_y, n_x, n_y)

        A = coo_matrix((values, (row, col))).tocsc()

    return A, rhs, f

def laplacian_1_Neumann(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1
    b = 1
    alpha = 0
    beta = 0
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y)

def laplacian_2_Neumann(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1
    b = 1
    alpha = 0
    beta = 0
    exact = sp.sin(sp.pi*x)*sp.sin(sp.pi*y)
    return construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y)

def equation_1_Neumann(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1 + sp.cos(x*y*sp.pi)
    alpha = sp.exp(x*y)
    b = sp.exp(-x*y) + 1
    beta = 1 + sp.sin(2*(x+y)*sp.pi)**2
    exact = sp.exp(-x+2*y)
    return construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y)

def equation_2_Neumann(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1 + sp.cos(x*y*sp.pi)
    alpha = sp.exp(x*y)
    b = sp.exp(-x*y) + 1
    beta = 1 + sp.sin(2*(x+y)*sp.pi)**2
    exact = x**5 + y**2 + 3
    return construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y)

def equation_3_Neumann(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1 + sp.cos(x*y*sp.pi) + x**2
    alpha = sp.exp(x*y)
    b = sp.exp(-x*y) + sp.exp(x*y) + 1
    beta = 1 + sp.sin(2*(x+y)*sp.pi)**2 + y**2
    exact = x**5 + y**2*sp.cos(x*y*2*sp.pi) + 3
    return construct_equation_Neumann(a, b, alpha, beta, exact, x, y, L_x, L_y)

def laplacian(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1
    b = 1
    alpha = 0
    beta = 0
    q = 0
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def epsilon_laplacian(L_x, L_y, epsilon):
    x, y = sp.symbols('x, y', real=True)
    a = 1
    b = epsilon
    alpha = 0
    beta = 0
    q = 0
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def laplacian_2(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1
    b = 1
    alpha = 0
    beta = 0
    q = 0
    exact = sp.sin(sp.pi*x)*sp.sin(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_1(L_x, L_y, alpha):
    x, y = sp.symbols('x, y', real=True)
    a = sp.exp(-x*y) + alpha
    b = sp.exp(-2*x+2*y) + sp.exp(2*x-2*y)
    alpha = sp.cos(sp.pi*(x + y/2)) + 4
    beta = sp.exp(2*x - 2*y)
    q = 0
    exact = x**2 + y**4 - x*y*2 + 1
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_2(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = sp.exp(-x*(y+2)) + 10
    b = sp.exp(-2*x+2*y)*sp.cos(2*sp.pi*(2*x + y/2))**2 + 3
    alpha = sp.cos(sp.pi*(x + y/2))*sp.cos(2*sp.pi*(x)) + 4
    beta = sp.exp(2*x - 2*y)
    q = 0
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_3(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = sp.exp(-x*y) + 10
    b = sp.exp(-2*x+2*y)
    alpha = sp.cos(sp.pi*(x + y/2)) + 4
    beta = sp.exp(2*x - 2*y)
    q = 0
    exact = sp.exp(x*y)*sp.cos(4*sp.pi*(x+2*y))
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_4(L_x, L_y, alpha):
    x, y = sp.symbols('x, y', real=True)
    a = sp.exp(-x*(y+2)) + alpha
    b = sp.cos(2*sp.pi*(2*x + y/2)) + 4
    alpha = sp.cos(sp.pi*(x + y/2))*sp.cos(2*sp.pi*(x))
    beta = sp.exp(2*x - 2*y)
    q = 0
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_5(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = 1 - sp.cos(4*sp.pi*(x+y))
    b = 1 + sp.cos(4*sp.pi*(x+y))
    alpha = 0
    beta = 0
    q = sp.sin(4*sp.pi*(x+y))**2
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)

def equation_6(L_x, L_y):
    x, y = sp.symbols('x, y', real=True)
    a = sp.exp(-x*y) + 1
    b = sp.exp(-2*x+2*y)
    alpha = sp.cos(sp.pi*(x + y/2)) + 4
    beta = sp.exp(2*x - 2*y)
    q = sp.exp(-3*x-4*y)
    exact = sp.cos(sp.pi*x)*sp.cos(sp.pi*y)
    return construct_equation(a, b, alpha, beta, q, exact, x, y, L_x, L_y)
