@echo off
for %%n in (SYS, SCR, FIN, LST, KIR, DAT, PMC, h5i, h5v, h5d, h5m) do del VVER.%%n*
del warnings.txt
echo on
"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"  -n 8 ..//kir_ed.exe %1 