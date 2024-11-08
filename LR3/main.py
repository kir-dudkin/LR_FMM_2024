import numpy as np

from KirClass import *
from materials import *
import matplotlib.pyplot as plt

PROJECT_NAME = "VVER"
LIB = r"D:\KIR_ed\KIR_LIB\e-71.njoy.tpc-ed.hdf\cfg_tpc"

KIR = KirProgram(project_name=PROJECT_NAME, library_path=LIB)

N_regions = 10


def write_cell(n_reg, NTOT):
    with open(KIR.kir_input_path, "w") as f:
        f.write("HEAD  1  0  10000\nCONT B B T T T T T T\n"
                "EQU H= 370.0\n"
                f"EQU Hreg= 370.0/{n_reg}\n\n"
                "HEXY Water 0.0 0.0 0.0 H 12.75/10\n")
        f.write("RCZ Clad 0 0 0 H 9.1/20\nRCZ Gap 0 0 0 H (9.1 - 0.65 * 2)/20\n")
        for i in range(n_reg):
            f.write(
                f"RCZ Fuel{i + 1} 0 0 Hreg*{i} Hreg (9.1 - (0.65 + 0.075) * 2)/20\n")
        f.write("END\n\nZWATER Water -Clad # m = 1\nZCLAD Clad -Gap # m = 2\n")
        f.write(f"ZGAP Gap")
        for i in range(n_reg):
            f.write(f" -Fuel{i + 1}")
        f.write(" # m = 3\n")
        for i in range(n_reg):
            f.write(f"ZF{i + 1} Fuel{i + 1} # m = {i + 4} z = {i + 2}\n")
        f.write("END")
    KIR.write_end_of_file(regions=n_reg + 1, estimation="c", NTOT=NTOT, NSKI=250, MSXR=550)


def read_regions_data(n_reg, qv):
    n_regions = int(n_reg)
    FLAG = "STD Functionals Block # 1"
    with open(KIR.kir_output_path + ".FIN", "r") as f:
        lines = f.readlines()
        counter = 0
        for line in lines:
            sline = line.strip()
            if sline == FLAG:
                break
            counter += 1
        arr = []

        for i in range(1, n_regions + 1):
            reg = lines[counter + 8 + i].split()
            arr += [float(reg[1])]
        s_kz = sum(arr)/len(arr)
        qv_arr = [a / s_kz * qv for a in arr]
    print(qv_arr)
    return qv_arr


def write_physics(T_list):
    with open("./input/physics.dat", "w") as f:
        f.write(KIR.lib_path)
        f.write("\n")
        water(1, 300 + 273, f)
        e110(2, 800, f)
        he(3, 1500, f)
        for i in range(len(T_list)):
            UO2(4 + i, T_list[i], f, 0.01)


def plot_kz_of_NTOT(NTOT_list):
    x = np.linspace(0, 3.7, N_regions)
    for NTOT in NTOT_list:
        write_cell(N_regions, NTOT)
        T = [300] * N_regions
        write_physics(T_list=T)
        KIR.run_kir(check_code=True)
        kz = read_regions_data(N_regions, qv=1)
        plt.plot(x, kz, label=f"NTOT={NTOT}")
    plt.grid()
    plt.legend()
    plt.xlabel("Высота твела")
    plt.ylabel("Относительное энерговыделение")

    out_path = "./output"
    if os.path.exists(out_path):
        pass
    else:
        os.mkdir(out_path)
    plt.savefig(out_path + "/plot.png")
    plt.show()


if __name__ == '__main__':
    KIR.write_KIR_FILES()
    NTOTs = [10, 100, 500, 1000]
    plot_kz_of_NTOT(NTOT_list=NTOTs)
