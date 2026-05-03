# Kill process on port 8000
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    $procId = $conn.OwningProcess | Select-Object -First 1
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}
# Start backend
Start-Process python -ArgumentList '-m','uvicorn','main:app','--reload' -WorkingDirectory 'D:\ai-carbon-system\backend' -WindowStyle Hidden -PassThru
Start-Sleep 3
