echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 54484 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14524) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24416) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 8396) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 23316) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 23692) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 19768) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 17452) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 400) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 21600) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 18420)
del "E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-21600.bat"
