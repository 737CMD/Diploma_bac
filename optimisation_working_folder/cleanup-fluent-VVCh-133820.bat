echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 60721 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 124624) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 129192) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 133804) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 50908) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 112560) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 108984) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 121192) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 64904) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 115192) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 100068) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 133820) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 121084)
del "e:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-133820.bat"
