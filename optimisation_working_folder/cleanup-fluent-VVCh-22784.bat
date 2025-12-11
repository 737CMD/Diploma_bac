echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 57747 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 3364) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 10724) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 7072) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22372) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 21408) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 10708) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 7408) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 8900) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22004) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 9516) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22784) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 19584)
del "E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-22784.bat"
