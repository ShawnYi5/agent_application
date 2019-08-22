@setlocal enableextensions enabledelayedexpansion

del /q .\js\*.js
del /q .\cpp\*.h
del /q .\cpp\*.cpp

for %%s in (.\*.ice) do ( 
.\bin\slice2js  %%s --output-dir .\js -I"slice" 
.\bin\slice2cpp %%s  --output-dir .\cpp -I"slice"  
.\bin\3.5_vc100\slice2cpp %%s  --output-dir .\cpp\3.5 -I".\slice\3.5"
) 

rd /s /q .\py
md .\py

set files=
  for %%s in (.\*.ice) do set files=!files! %%s

.\bin\slice2py --output-dir .\py -I"slice" %files%
py -3.6 C:\Python36\Scripts\slice2py-script.py --output-dir .\py -I"slice" %files%

pause
