Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ArgsPassthrough
)

$ErrorActionPreference = "Stop"

# 1) Create venv if missing
if (!(Test-Path -Path "venv")) {
    & python -m venv venv
}

# 2) Activate venv
$activate = ".\venv\Scripts\Activate.ps1"
. $activate

# 3) Install requirements (if file exists)
if (Test-Path -Path "requirements.txt") {
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

# 4) Ensure .env exists
if (!(Test-Path -Path ".env") -and (Test-Path -Path ".env.example")) {
    Copy-Item ".env.example" ".env" -Force
    Write-Host "[make.ps1] .env criado a partir de .env.example - ajuste os valores conforme necessário."
}

# 5) Run the app (pass-through args, e.g., --scheduled --interval 10)

            # Parse flags
            $VerboseFlag = $false
            $InitDbFlag = $false
            $ForwardArgs = @()

            foreach ($a in $ArgsPassthrough) {
                if ($a -eq "--verbose") { $VerboseFlag = $true }
                elseif ($a -eq "--init-db") { $InitDbFlag = $true }
                else { $ForwardArgs += $a }
            }

            if ($VerboseFlag) {
                $env:LOG_LEVEL = "DEBUG"
                Write-Host "[make.ps1] LOG_LEVEL=DEBUG"
            }

            if ($InitDbFlag) {
                Write-Host "[make.ps1] Inicializando banco de dados..."
                python .\scripts\init_db.py
            }

            python ".\src\main.py" @ForwardArgs

