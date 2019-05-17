docker build -t codec .

docker run -d  --restart=always \
     --name codec \
     -p 7002:7002 \
     codec