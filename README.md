# nsls2api


podman build -t nsls2api .

podman run -d --name apicontainer -v ./nsls2api/.env:/code/.env -p 8090:80 nsls2api