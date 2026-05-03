Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Set-Location D:\ai-carbon-system\backend
Start-Process -FilePath 'python' -ArgumentList '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8000' -WindowStyle Hidden
Start-Sleep -Seconds 4
$req = [System.Net.WebRequest]::Create('http://127.0.0.1:8000/api/v1/carbon/company/')
$resp = $req.GetResponse()
Write-Host "backend status: $($resp.StatusCode)"
