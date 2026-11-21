@echo off
call "%~dp0tools\QGIS\bin\o4w_env.bat"
set PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\Qt5\plugins
"%OSGEO4W_ROOT%\bin\qgis-ltr-bin.exe" --postinstall
