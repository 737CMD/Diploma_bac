echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 62301 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16952) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22020) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14744) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 11704) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 33804) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24980) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 15540) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22144) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 21420) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 3824) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16840) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14380)
del "E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-16840.bat"
