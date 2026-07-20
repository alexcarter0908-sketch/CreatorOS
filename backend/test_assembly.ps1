# 1) Login - OAuth2PasswordRequestForm expects form-urlencoded body with "username"/"password"
$loginResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
    -Method Post `
    -Body @{ username = "test@example.com"; password = "testpass123" } `
    -ContentType "application/x-www-form-urlencoded"

$token = $loginResp.access_token
Write-Host "Token: $token"

if (-not $token) {
    Write-Host "LOGIN FAILED - stopping."
    exit
}

# 2) Assembly request - public sample clips
$assemblyBody = @{
    clips = @(
        @{ url = "https://download.samplelib.com/mp4/sample-5s.mp4"; order = 1 },
        @{ url = "https://download.samplelib.com/mp4/sample-10s.mp4"; order = 2 }
    )
    burn_captions = $false
} | ConvertTo-Json -Depth 5

$headers = @{ Authorization = "Bearer $token" }

$renderResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/assembly/render" -Method Post -Body $assemblyBody -ContentType "application/json" -Headers $headers
Write-Host "=== Render response ==="
$renderResp

# 3) Poll asset status every 5s, up to 12 times (60s)
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 5
    $asset = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/assets/$($renderResp.asset_id)" -Headers $headers
    Write-Host "Poll $i - status: $($asset.status)"
    if ($asset.status -eq "completed" -or $asset.status -eq "failed") {
        $asset
        break
    }
}