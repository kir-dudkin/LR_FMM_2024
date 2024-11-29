from KirClass import *

PROJECT_NAME = "SP"
LIB = r"W:\KIR_LIB\e-71.njoy.tpc-ed.hdf\e-71.njoy.tpc-ed.hdf\cfg_tpc"
KIR_EXE = r"W:\KIR\kir_ed.exe"

KIR = KirProgram(project_name=PROJECT_NAME, library_path=LIB, KIR_path=KIR_EXE)

if __name__ == '__main__':
    #KIR.write_KIR_FILES(n_interval=24)
    #KIR.run_kir()
    KIR.read_spectr()



