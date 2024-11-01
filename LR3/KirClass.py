import os
import shutil
from pathlib import Path
import subprocess

SOURCE_PATH = "./input/"
TARGET_PATH = "./"


def copyfile(source_dir, target_dir, filename):
    shutil.copyfile(source_dir + filename, target_dir + filename)
    return 0


class KirProgram:
    def __init__(self, project_name, library_path, MPI_path=None):

        self.project = project_name
        self.kir_input_path = SOURCE_PATH + self.project
        self.kir_output_path = TARGET_PATH + self.project

        abs_path = "empty"
        try:
            abs_path = Path("..//kir_ed.exe").resolve(strict=True)
        except FileNotFoundError:
            print("Неправильно выбрана директория размещения проекта")
            print(abs_path)
            exit(-1)
        else:
            pass

        if MPI_path is None:
            self.mpi_path = r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
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

    def write_KIR_FILES(self, target_dir=TARGET_PATH):
        with open(target_dir + "KIR.INI", "a") as f:
            f.write(self.project + "  \n\n")
            f.close()

        with open(target_dir + "mpi_kir2.bat", "w") as f:
            f.write(f"@echo off\n")
            f.write("for %%n in (SYS, SCR, FIN, LST, KIR, DAT, PMC, h5i, h5v, h5d, h5m) ")
            f.write(f"do del {self.project}.%%n*\ndel warnings.txt\necho on\n")
            f.write("\"" + self.mpi_path + "\" " + " -n 8 ..//kir_ed.exe %1 ")
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
                f.write("HEAD  1  0  10000\nCONT B B B\n")
                f.write("EQU H= 50.0\n")
                f.write("RCZ Fuel 0 0 0 H 10\nEND\nZFUEL Fuel # m = 1\nEND")
            self.write_end_of_file()
            print("Файл исходных данных создан")

        if os.path.isfile(physics_input_path):
            print("Файл физики уже существует и не будет перезаписан")
        else:
            with open(physics_input_path, "w") as f:
                f.write(self.lib_path + '\n')
                f.write("# 1 Fuel\nT=300\n2.0E-03 U238\n3.0E-02 U235\n")
                f.close()
            print("Файл физики создан")
        return 0

    def write_end_of_file(self, regions=1, estimation="t", NTOT=200, NSKI=50, MSXR=250):
        with open(self.kir_input_path, "a") as f:
            f.write("\n\nFINISH\n*\nRRS\nSOURCE 1\nS NAME=S1 SPECTRUM=SP1 PNT 0 0 20\nEND SOURCE\n")
            f.write("SPECTRUM SP1\nENERGY\n 2E6\nPROBABILITY\n 1.0\nEND SPECTRUM SP1\nFINISH RRS\nRUGA\nKEFF\n")
            if regions == 1:
                str_reg = "REGION 1"
            elif regions > 1:
                str_reg = f"REGION L1R{regions}"
            else:
                raise Exception("Некорректное число регионов")
            f.write(f"REGTYPE STD\nESTIMATION {estimation}\n{str_reg}\nENERGY 0\nEND\nFINISH\n")
            f.write(f"NTOT {NTOT}\nNSKI {NSKI}\nFINISH\nNAMV {self.project}\nMXSR {MSXR}\nDTZM 50\nFINISH\n")

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
