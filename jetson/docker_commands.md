## build image
### pick directory in question

cd [path here]

### build docker image
docker build -t testimage -f Dockerfile_camera .

## run image 
docker run -it --rm --device /dev/video0 --network host -e DISPLAY=$DISPLAY testimage 
