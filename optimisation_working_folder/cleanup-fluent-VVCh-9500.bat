echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 51408 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 36448) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 30564) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 4304) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 35564) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 33752) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 17656) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 27060) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 4672) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14044) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 20292) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 9500) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 28548)
del "e:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-9500.bat"
