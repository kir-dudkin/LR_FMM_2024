from datetime import datetime
import matplotlib.pyplot as plt
from LR1_script import *

PROJECT_NAME = "SNRE_FUEL"
KIR_PROJECT_PATH = "D:/KIR_ed/KIR/LR2/"
KIR_LIB_PATH = r"D:\KIR_ed\KIR_LIB\e-71.njoy.tpc-ed.hdf\cfg_tpc"
R = 8.31
N_a = 6.022e23

Zr_ISOTOPES = {"Zr90":0.5145, "Zr91":0.1122, "Zr92":0.1715, "Zr94":0.1738, "Zr96":0.028}

write_KIR_FILES(KIR_PROJECT_PATH, PROJECT_NAME)



def write_hydrogen(p, T, num, file):
    mu_h2 = 2e-3
    R = 8.31
    R_mu = R/mu_h2
    rho = p / (R_mu * T)
    N = rho * N_a / mu_h2 * 1e-30
    file.write(f"\n# {num} Hydrogen\nT={T}\n")
    file.write('{:.3E}'.format(N) + " H1\n")

def write_fuel(x, T, num, file):
    # Тройной раствор {U_x + Zr_(1-x)}C_y // x = 0.1, y = 0.98
    St_C = 1.98
    St_U = 0.2
    St_Zr = 1 - St_U
    mu_UZrC = (235.2 * St_U + 91 * St_Zr + 12 * St_C)* 1e-3
    rho_fuel = 3640
    N = rho_fuel * N_a / mu_UZrC * 1e-30
    file.write(f"\n# {num} Fuel\nT={T}\n")
    file.write('{:.3E}'.format(N*St_C) + " C12 | GRAPHITE\n")
    file.write('{:.3E}'.format(N*St_U * (1-x)) + " U238\n")
    file.write('{:.3E}'.format(N * St_U * x) + " U235\n")
    for k, v in Zr_ISOTOPES.items():
        file.write('{:.3E}'.format(N * St_Zr * v) + f" {k}\n")

def write_ZrC(TD, T, num, file):
    # Карбид циркония ZrC_0.81
    mu_ZrC = (91 + 0.81 * 12) * 1e-3
    rho_ZrC = TD * 5900
    N = rho_ZrC * N_a / mu_ZrC * 1e-30
    file.write(f"\n# {num} ZrC (TD={int(TD*100)}%)\nT={T}\n")
    file.write('{:.3E}'.format(N*0.81) + " C12 | GRAPHITE\n")
    for k, v in Zr_ISOTOPES.items():
        file.write('{:.3E}'.format(N * v) + f" {k}\n")


def write_physics_dat(param=None):
    with open("./input/physics.dat", "w") as f:
        f.write(KIR_LIB_PATH + '\n')
        write_hydrogen(10e6, param, 1, f)
        write_fuel(x=0.93, T=300, num=2, file=f)
        write_ZrC(TD=0.5, T=300, num=3, file=f)
        write_ZrC(TD=1.0, T=300, num=4, file=f)
        f.close()

def read_keff(write_to_file=True, clear_file_before_run=True):
    FLAG = "Keff by t/c/a/f"
    with open(KIR_PROJECT_PATH + PROJECT_NAME + ".FIN") as f:
        lines = f.readlines()
        counter = 0
        for line in lines:
            sline = line.strip()
            if sline == FLAG:
                break
            else:
                counter+=1
        keff = float(lines[counter + 1].strip())
        k_err_txt = lines[counter + 2].strip()
        k_err = float(k_err_txt.split()[1])


    if write_to_file:
        if not os.path.exists("./output"):
            os.mkdir("./output")

        if clear_file_before_run:
            open('./output/keff.txt', 'w').close()

        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        with open("./output/keff.txt", "a") as f:
            f.write(f"{keff} +- {k_err} // at time " +str(current_datetime) +"\n")

    return keff, k_err

def plot_Keff_of_T():
    t_list = [300, 600, 900, 1200, 1500]
    k_eff_list = []
    k_err_list = []
    clear = True
    for T in t_list:
        write_physics_dat(T)
        copy_input_files(KIR_PROJECT_PATH, PROJECT_NAME)
        run_kir(KIR_PROJECT_PATH)
        data = read_keff(clear_file_before_run=clear)
        k_eff_list += [data[0]]
        k_err_list += [data[1]]
        clear=False

    plt.errorbar(t_list, k_eff_list, yerr=k_err_list, capsize=3, fmt="r--o", ecolor="black")
    plt.grid()
    plt.xlabel("Температура, К")
    plt.xlabel ("k_eff")
    plt.show()
write_physics_dat(1500)
run_kir(TARGET_PATH)