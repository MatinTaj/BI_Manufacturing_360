[CmdletBinding()]
param([switch]$Execute)
$ErrorActionPreference='Stop'
$ProjectRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$StagePath=Join-Path $ProjectRoot 'data/staging'
$Manifest=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '../input_manifest.json') | ConvertFrom-Json
foreach($Property in $Manifest.datasets.PSObject.Properties){
 $Entry=$Property.Value
 $Path=Join-Path $StagePath $Entry.file
 if((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Entry.sha256){throw "Staging hash mismatch: $($Entry.file)"}
 if(((Get-Content -LiteralPath $Path -TotalCount 1) -split ',' -join ',') -cne ($Entry.columns -join ',')){throw 'CSV header mismatch'}
}
$Baseline=Join-Path (Join-Path $ProjectRoot $Manifest.phase7_report) 'financial_comparison.csv'
if((Get-FileHash -LiteralPath $Baseline -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Manifest.phase7_financial_sha256){throw 'Phase 7 reference changed'}
if(-not $Execute){Write-Output 'PLAN ONLY: manufacturing_360.manufacturing_v2, 19 approved CSVs; no connection.';return}
$Psql='C:/Program Files/PostgreSQL/18/bin/psql.exe'
$Arguments=@('-X','-w','-h','localhost','-p','5432','-U','postgres','-d','manufacturing_360','-v','ON_ERROR_STOP=1')
Push-Location -LiteralPath $StagePath
try{
 & $Psql @Arguments -f (Join-Path $PSScriptRoot 'apply.psql')
 if($LASTEXITCODE -ne 0){throw 'Migration failed; stop and inspect output. No automatic retry.'}
}finally{Pop-Location}
