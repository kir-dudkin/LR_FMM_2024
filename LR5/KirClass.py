import os
import shutil
from pathlib import Path
import subprocess
import numpy as np
import matplotlib.pyplot as plt

SOURCE_PATH = "./input/"
TARGET_PATH = "./"


def copyfile(source_dir, target_dir, filename):
    shutil.copyfile(source_dir + filename, target_dir + filename)
    return 0


class KirProgram:
    def __init__(self, project_name, library_path, MPI_path=None, KIR_path="..//kir_ed.exe"):

        self.project = project_name
        self.kir_input_path = SOURCE_PATH + self.project
        self.kir_output_path = TARGET_PATH + self.project
        self.kir_exe_path = KIR_path

        abs_path = "empty"
        try:
            abs_path = Path(self.kir_exe_path).resolve(strict=True)
        except FileNotFoundError:
            print("Неправильно выбрана директория размещения проекта")
            print(abs_path)
            exit(-1)
        else:
            pass

        if MPI_path is None:
            self.mpi_path = r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
        else:
            self.mpi_path = MPI_path
        abs_path = None
        try:
            abs_path = Path(self.mpi_path).resolve(strict=True)
        except FileNotFoundError:
            print("Неправильно указан путь к mpiexec.exe:")
            print(abs_path)
        else:
            pass

        self.lib_path = library_path

        if os.path.isfile(self.lib_path + "default.phm") or os.path.isfile(self.lib_path + "/default.phm"):
            pass
        else:
            raise FileNotFoundError("Неправильно указан путь к библиотекам КИР")

    def write_KIR_FILES(self, target_dir=TARGET_PATH, regions=1, estimation="t", NTOT=200, NSKI=150, MSXR=350,
                        spectr=True, spectr_regzone=1, n_interval=24, E_max=10e6):
        with open(target_dir + "KIR.INI", "w") as f:
            f.write(self.project + "  \n\n")
            f.close()

        with open(target_dir + "mpi_kir2.bat", "w") as f:
            f.write(f"@echo off\n")
            f.write("for %%n in (SYS, SCR, FIN, LST, KIR, DAT, PMC, h5i, h5v, h5d, h5m) ")
            f.write(f"do del {self.project}.%%n*\ndel warnings.txt\necho on\n")
            f.write("\"" + self.mpi_path + "\" " + f" -n 8 {self.kir_exe_path} %1 ")
            f.close()

        project_input_path = SOURCE_PATH + self.project
        physics_input_path = SOURCE_PATH + "physics.dat"

        if os.path.exists(SOURCE_PATH):
            pass
        else:
            os.mkdir(SOURCE_PATH)

        if os.path.isfile(project_input_path):
            print("Файл исходных данных существуют и не будет перезаписан")
        else:
            with open(project_input_path, "w") as f:
                f.write("HEAD  1  0  10000\nCONT B B T T T T T T\n")
                f.write("EQU H= 50.0\n")
                f.write("HEXY MDR 0 0 0 H 20\nRCZ Fuel 0 0 0 H 8\nEND\nZMDR MDR -Fuel # m = 2\nZFUEL Fuel # m = 1\nEND")
                f.write("\n\nFINISH\n*\nRRS\nSOURCE 1\nS NAME=S1 SPECTRUM=SP1 PNT 0 0 20\nEND SOURCE\n")
                f.write("SPECTRUM SP1\nENERGY\n 2E6\nPROBABILITY\n 1.0\nEND SPECTRUM SP1\nFINISH RRS\nRUGA\nKEFF\n")
                if regions == 1:
                    str_reg = "REGION 1"
                elif regions > 1:
                    str_reg = f"REGION L1R{regions}"
                else:
                    raise Exception("Некорректное число регионов")
                f.write(f"REGTYPE STD\nESTIMATION {estimation}\n{str_reg}\nENERGY 0\nEND\n")

                if spectr:
                    sp_energy = np.logspace(-4, np.log10(E_max), num=n_interval)
                    f.write(f"\nREGTYPE STD\nESTIMATION c\nREACTION 0\nREGION {spectr_regzone}\nENERGY")
                    for E in list(sp_energy):
                        f.write(f"\n {E}")
                    f.write("\nSORT TIME ISOTOPE REACTION  ESTIMATION DOMAIN ENERGY\nEND\n")

                f.write(
                    f"\nFINISH\nNTOT {NTOT}\nNSKI {NSKI}\nFINISH\nNAMV {self.project}\nMXSR {MSXR}\nDTZM 50\nFINISH\n")

            print("Файл исходных данных создан")

        if os.path.isfile(physics_input_path):
            print("Файл физики уже существует и не будет перезаписан")
        else:
            with open(physics_input_path, "w") as f:
                f.write(self.lib_path + '\n')
                f.write("# 1 Fuel\nT=300\n2.0E-03 U238\n3.0E-03 U235\n\n")
                f.write("# 2 MDR\nT=300\n6.0E-02 H1\n3.0E-02 016\n")

                f.close()
            print("Файл физики создан")
        return 0

    def copy_input_files(self, target_dir=TARGET_PATH):
        copyfile(SOURCE_PATH, target_dir, self.project)
        copyfile(SOURCE_PATH, target_dir, "physics.dat")
        return 0

    def run_kir(self, target_dir=TARGET_PATH, check_code=False):

        self.copy_input_files()

        if check_code:
            pipe = subprocess.PIPE
        else:
            pipe = None

        run_kir_exe = subprocess.Popen(args="mpi_kir2.bat", cwd=target_dir, stdout=pipe, stderr=pipe)

        if check_code:
            out, err = run_kir_exe.communicate()
            if err:
                print("standard error of subprocess:")
                print(err)
            rcode = run_kir_exe.returncode
            print("returncode of kir_ed subprocess:", rcode)
            if rcode == 0:
                print("Программа КИР работает корректно")
        else:
            run_kir_exe.wait()

    def read_kir_data(self):
        FLAG = "Keff with minimal sdt.dev. is:"
        with open(self.kir_output_path + ".FIN", "r") as f:
            lines = f.readlines()
            counter = 0
            for line in lines:

                sline = line.strip()
                if sline == FLAG:
                    break
                counter += 1
            k_eff_s = lines[counter + 3]
            k_err_s = lines[counter + 4]

            k_eff = float(k_eff_s)
            k_err_split = k_err_s.split()[1]
            k_err = float(k_err_split)
            print("Keff =", k_eff)
            print("Kerr =", k_err)
            return k_eff, k_err

    def read_spectr(self, plot=True, energy_cut_off=2e7, saveplot=True):
        with open(f"./{self.project}.FIN", "r") as f:
            lines = f.readlines()
            k = 0
            c = 0
            start = -99
            for line in lines:
                k += 1
                sline = line.strip()
                if sline == "Energy":
                    start = k + 0
                    break
            while sline != "_______________________________________________":
                c += 1
                sline = lines[start + c].strip()
                stop = start + c

        kir_spectr = lines[start:stop]

        with open("./output/#SPECTR_OUTPUT.txt", "w") as f:
            f.writelines(kir_spectr)


        energy = []
        flux_value = []
        for line in kir_spectr:
            split_line = line.split()
            energy += [float(split_line[0])]
            flux_value += [float(split_line[1])]

        energy += [energy_cut_off]
        lethargy = []
        normalized_value = []
        for i in range(len(energy)-1):
            lnU = np.log(energy[i+1] / energy[i])
            lethargy += [lnU]
            normalized_value += [flux_value[i] / lnU]

        x = energy[1:]
        height = normalized_value

        plt.xscale("log")
        widths = np.diff(energy)
        plt.bar(x, height, widths, align='edge', facecolor='dodgerblue', edgecolor='white', lw=0.1)
        plt.xlabel("Энергия нейтрона , эВ")
        plt.ylabel("Нормированный удельный поток")
        plt.grid()

        if saveplot:
            plt.savefig("./output/spectr.png")
        if plot:
            plt.show()











