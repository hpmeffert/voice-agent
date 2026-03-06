@echo off
setlocal

cd /d C:\Install\voice-agent

REM ---- choose deploy branch ----
set BRANCH=v5-azure-hybrid

echo Fetching...
git fetch --all --tags

echo Checking working tree...
for /f %%i in ('git status --porcelain') do (
  echo ERROR: Local changes detected. Aborting.
  git status
  exit /b 1
)

echo Switching to %BRANCH%...
git checkout %BRANCH% || exit /b 1

echo Pulling latest (fast-forward only)...
git pull --ff-only origin %BRANCH% || exit /b 1

echo Rebuilding / restarting containers...
docker compose --env-file .env -f docker/compose.azure-hybrid.yml up -d --build

echo Done.
endlocal
