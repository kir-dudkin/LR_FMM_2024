### TEST RUN ###
import subprocess

RUN_DIR = r"D:/KIR_ed/KIR/test/"
RUN_KIR_COMMAND = RUN_DIR + "mpi_kir2.bat"
CLEAN_DIR_COMMAND = RUN_DIR + "remove.bat"

def test(check_code=False):
    if check_code:
        pipe = subprocess.PIPE
    else:
        pipe = None

    clean_dir_exe = subprocess.Popen(args=CLEAN_DIR_COMMAND, cwd=RUN_DIR)
    clean_dir_exe.wait()

    run_kir_exe = subprocess.Popen(args=RUN_KIR_COMMAND, cwd=RUN_DIR, stdout=pipe, stderr=pipe)
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

test(check_code=True)