$fnUrl = 'https://faas-nyc1-2ef2e6cc.doserverless.co/api/v1/web/fn-a1238ba0-5e45-4841-9c29-b7a40d9ef9a6/sample/hello'
$params = @{
    'name' = 'World'
}

# Convert params to query string
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
$fullUrl = "$fnUrl?$query"

# Invoke it
$result = Invoke-RestMethod -Uri $fullUrl -Method Get -Headers @{
    'Content-Type' = 'application/json'
    # "X-Require-Whisk-Auth" = "Dw18EJ7vxozL5pH"
}

# See what comes back
$result | Write-Host