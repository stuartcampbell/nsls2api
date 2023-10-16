# nsls2api


podman build -t nsls2api .

podman run --rm -d --name apicontainer --network=host --env-file=./nsls2api/.env nsls2api