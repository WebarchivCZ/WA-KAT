#!/usr/bin/env bash

# Make Bash Great Again
set -o errexit # exit when a command fails.
set -o nounset # exit when using undeclared variables
set -o pipefail # catch non-zero exit code in pipes
# set -o xtrace # uncomment for bug hunting

docker pull webarchiv/kat:{{docker_tag}}
docker rm -f wa-kat >/dev/null 2>&1 || /bin/true

docker run --restart=always -d \
 --name wa-kat \
 --label "traefik.http.routers.kat.rule=Host(\`kat.webarchiv.cz\`)" \
 --network seeder_default \
 webarchiv/kat:{{docker_tag}}

 