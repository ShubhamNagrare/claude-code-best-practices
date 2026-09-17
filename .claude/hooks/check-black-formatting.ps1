#!/usr/bin/env pwsh
<#
.SYNOPSIS
Post-Claude hook: Check and auto-format Python files with black
Runs after Claude writes/edits Python files to ensure consistent formatting
#>

param(
    [Parameter(ValueFromPipeline = $true)]
    [string]$InputJson
)

try {
    $data = $InputJson | ConvertFrom-Json
    $file = $data.tool_input.file_path

    if ($file -and $file -like "*.py") {
        Write-Host "📋 Checking black formatting: $file" -ForegroundColor Cyan

        # Run black with check mode first to see if formatting is needed
        $checkResult = & uv run black --check --quiet $file 2>&1
        $checkExitCode = $LASTEXITCODE

        if ($checkExitCode -ne 0) {
            Write-Host "⚠️  Formatting issues detected. Running black to fix..." -ForegroundColor Yellow
            & uv run black --quiet $file
            Write-Host "✅ File formatted with black" -ForegroundColor Green
        }
        else {
            Write-Host "✅ File is properly formatted" -ForegroundColor Green
        }
    }
}
catch {
    Write-Host "❌ Hook error: $_" -ForegroundColor Red
}
