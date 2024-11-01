
N_a = 6.022e23


def water(num, T, file):
    rho_w = 750
    mu_w = 18e-3
    N_w = rho_w * N_a / mu_w * 1e-6 * 1e-24
    file.write(f"\n# {num} water\nT={T}\n")
    file.write("{:.3E}".format(N_w) + " O16\n")
    file.write("{:.3E}".format(N_w * 2) + " H1\n")


def e110(num, T, file):
    ZR_ISOTOP = {"Zr90": 0.5145, "Zr91": 0.1122, "Zr92": 0.1715, "Zr94": 0.1738, "Zr96": 0.028}
    rho_e110 = 6100
    mu_zr = 92e-3
    N_zr = rho_e110 * N_a / mu_zr * 1e-30
    file.write(f"\n# {num} E110\nT={T}\n")
    for k, v in ZR_ISOTOP.items():
        file.write("{:.3E}".format(N_zr * v) + f" {k}\n")


def he(num, T, file):
    p = 12e6

    mu_he = 4e-3

    rho_he = p * mu_he / (8.31 * T)

    N_w = rho_he * N_a / mu_he * 1e-6 * 1e-24
    file.write(f"\n# {num} He\nT={T}\n")
    file.write("{:.3E}".format(N_w) + " He4\n")


def UO2(num, T, file, x):
    rho = 10400
    mu_U02 = (16 * 2 + 238) * 1e-3
    N = rho * N_a / mu_U02 * 1e-30
    file.write(f"\n# {num} U02\nT={T}\n")
    file.write('{:.3E}'.format(N * 2) + " O16\n")
    file.write('{:.3E}'.format(N * (1 - x)) + " U238\n")
    file.write('{:.3E}'.format(N * x) + " U235\n")
    return 0







