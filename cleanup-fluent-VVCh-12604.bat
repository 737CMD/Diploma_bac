echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 65331 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 25800) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 27608) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 18412) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 17532) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14476) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14388) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 23788) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16936) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 24028) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 13044) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 12604) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 28564)
del "E:\tsagi_dipl\Diploma_bac\cleanup-fluent-VVCh-12604.bat"
