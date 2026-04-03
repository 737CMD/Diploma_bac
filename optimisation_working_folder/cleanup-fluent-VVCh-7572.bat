echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="E:\Program files\ANSYS Inc\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\tell.exe" VVCh 62053 CLEANUP_EXITING
timeout /t 1
"E:\Program files\ANSYS Inc\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 32920) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 18304) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 35268) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 22192) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 36988) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 26536) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 30272) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 30560) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 34824) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 14652) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 9964) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 16612) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 7572) 
if /i "%LOCALHOST%"=="VVCh" (%KILL_CMD% 6264)
del "E:\tsagi_dipl\Diploma_bac\optimisation_working_folder\cleanup-fluent-VVCh-7572.bat"
