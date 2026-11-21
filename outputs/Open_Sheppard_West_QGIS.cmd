@echo off
setlocal
set "PILOT_ROOT=%~dp0.."
set "PILOT_QGIS=%PILOT_ROOT%\work\tools\QGIS\bin\qgis-ltr-bin.exe"
if not exist "%PILOT_QGIS%" (
  echo Local QGIS runtime not found. Open the project in an installed QGIS.
  pause
  exit /b 1
)
start "" "%PILOT_QGIS%" --profiles-path "%PILOT_ROOT%\work\qgis_profiles" --profile default "%~dp0project\outputs\sheppard_west_pilot\corridor_01_pilot.qgz"
endlocal
