echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 59646 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 20616) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 6224) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24964) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22576) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14384) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 9568) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24664) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 25380) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 11872) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 23736) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 2220) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16448)
del "e:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-2220.bat"
