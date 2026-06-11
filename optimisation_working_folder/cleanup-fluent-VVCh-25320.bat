echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 56652 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 26320) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 28404) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 26432) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 27084) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16032) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 28044) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 27388) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24464) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 25320) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 25644)
del "E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-25320.bat"
