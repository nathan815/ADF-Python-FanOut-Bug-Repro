# primary parameters
$pw        = "pw123456"
$edition   = "Developer"
$port      = 1433
$tag       = "2019-latest"
$dbname    = "DurableDB"
$collation = "Latin1_General_100_BIN2_UTF8"

# pull the image from the Microsoft container registry
docker pull mcr.microsoft.com/mssql/server:$tag

# run the image and provide some basic setup parameters
# Check if the container is already running
if (-not (docker ps -q -f "name=mssql-server")) {
    # If not running, start the container
    docker rm mssql-server
    docker run --name mssql-server -v ./.mssql_data:/var/opt/mssql -e 'ACCEPT_EULA=Y' -e "MSSQL_SA_PASSWORD=$pw" -e "MSSQL_PID=$edition" -p ${port}:1433 -d mcr.microsoft.com/mssql/server:$tag
   
    # wait a few seconds for the container to start...
    Start-Sleep -Seconds 10
} else {
    Write-Host "Container 'mssql-server' is already running."
}

# create the database with strict binary collation
docker exec -d mssql-server /opt/mssql-tools18/bin/sqlcmd -S . -U sa -P "$pw" -Q "CREATE DATABASE [$dbname] COLLATE $collation"
