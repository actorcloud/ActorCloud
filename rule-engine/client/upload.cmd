@echo off
REM Script for windows to upload the output jars to remote
set SSHRSA=C:\Users\Administrator\.ssh\id_rsa.ppk
set PROJECT_PATH=D:\Workspace\incubator
set VERSION=0.5.3
set TARGET=root@139.198.189.110:/opt/stream

echo Start uploading
pscp -i %SSHRSA% -P 2222 -r %PROJECT_PATH%\target\%VERSION% %TARGET%