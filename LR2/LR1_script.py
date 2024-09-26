import os
import shutil
import subprocess

KIR_INPUT = "tvel_SNRE"
KIR_PHYS = "physics.dat"
SOURCE_PATH = "./input/"
TARGET_PATH = "D:/KIR_ed/KIR/LR1/"

def copyfile(source_dir, target_dir, filename):
    shutil.copyfile(source_dir + filename,target_dir + filename)
    return 0

def write_KIR_FILES(target_dir, project_name, rewrite_input=False):
    with open(target_dir + "KIR.INI", "w") as f:
        f.write(project_name +"  \n\n")
        f.close()

    with open(target_dir + "mpi_kir2.bat", "w") as f:
        f.write(f"@echo off\n")
        f.write("for %%n in (SYS, SCR, FIN, LST, KIR, DAT, PMC, h5i, h5v, h5d, h5m) ")
        f.write(f"do del {project_name}.%%n*\ndel warnings.txt\necho on\n")
        f.write(f"{r'"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"'} -n 4 ..//kir_ed.exe %1 ")

        f.close()

    if rewrite_input:
        project_input_path = SOURCE_PATH + project_name
        physics_input_path = SOURCE_PATH + "physics.dat"
        if os.path.isfile(project_input_path) or os.path.isfile(physics_input_path):
            print("Файлы уже существуют и не будут перезаписаны")
            return -1
        else:
            os.mkdir(SOURCE_PATH)
            with open(project_input_path, "w") as f:
                f.write("*KIR_DUMMY_FILE*")
                f.close()

            with open(physics_input_path, "w") as f:
                f.write("*PHYSICS.DAT_DUMMY_FILE*")
                f.close()
    return 0

def copy_input_files(target_dir, project_name):
    copyfile(SOURCE_PATH, target_dir, project_name)
    copyfile(SOURCE_PATH, target_dir, "physics.dat")
    return 0

def run_kir(target_dir, check_code=False):
    if check_code:
        pipe = subprocess.PIPE
    else:
        pipe = None

    run_kir_exe = subprocess.Popen(args=target_dir + "mpi_kir2.bat", cwd=target_dir, stdout=pipe, stderr=pipe)

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