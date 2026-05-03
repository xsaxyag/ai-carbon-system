$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$token = & 'D:\Qclaw\resources\openclaw\config\skills\github-skill\get-token.ps1'
$body = @{
  name = 'ai-carbon-system'
  description = 'AI碳枢算 - 中小微企业碳中和智能管理系统 (FastAPI + Vue3 + ECharts + RapidOCR + Groq LLM)'
  private = $false
} | ConvertTo-Json -Depth 10
$result = irm 'https://api.github.com/user/repos' -Method Post -Headers @{
  'Authorization' = "Bearer $token"
  'X-GitHub-Api-Version' = '2022-11-28'
  'Accept' = 'application/vnd.github+json'
} -ContentType 'application/json' -Body $body
Write-Output ($result | Select-Object full_name, html_url, clone_url | ConvertTo-Json)
