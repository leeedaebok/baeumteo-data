@echo off
REM 동네배움터 알리미 - 강좌 데이터 갱신 (수집 -> 변경 시 커밋/푸시)
REM 사용법: 이 파일이 있는 폴더에서 refresh.bat 실행.
REM   최초 1회 인증키를 아래에 넣거나, 시스템 환경변수 LEARNING_API_KEY 로 설정하세요.

cd /d "%~dp0"

if "%LEARNING_API_KEY%"=="" (
  REM 필요 시 아래 줄의 주석을 풀고 키를 직접 입력 (따옴표 없이)
  REM set LEARNING_API_KEY=여기에_data.go.kr_일반인증키_Decoding
)
if "%LEARNING_API_KEY%"=="" (
  echo [오류] 환경변수 LEARNING_API_KEY 가 설정되지 않았습니다.
  exit /b 1
)

echo [1/3] 강좌 수집...
python collect.py || (echo 수집 실패 & exit /b 1)

echo [2/3] 변경 확인...
git add data/courses.json
git diff --cached --quiet
if %errorlevel%==0 (
  echo   변경 없음 - 푸시 생략.
  exit /b 0
)

echo [3/3] 커밋 / 푸시...
for /f "tokens=*" %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH:mm"') do set NOW=%%d
git commit -m "data: refresh %NOW%"
git push
echo 완료.
