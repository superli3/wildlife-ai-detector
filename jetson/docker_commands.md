## build image
### pick directory in question

cd [path here]

### build docker image
docker build -t testimage -f Dockerfile_camera .

docker build -t testimage -f Dockerfile_camera --no-cache .

## run image 
docker run -it --gpus all --rm --device /dev/video0 --network host -e DISPLAY=$DISPLAY testimage2
