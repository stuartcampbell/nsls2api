# nsls2api


podman build -t nsls2api .

podman run --rm -d --name apicontainer --network=host --env-file=./nsls2api/.env -p 9092:8080 nsls2api