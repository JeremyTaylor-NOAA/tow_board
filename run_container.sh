# IMPORTANT NOTE:
#   - This file is necessary on the first run of a MOUSS_mini on a new system!!!
#   - However, <docker compose up> should be used in production situations
# This is a  file designed to help run the mouss_mini docker container
# to help rapid development. This run command uses a volume mount so that 
# changes in (only) /mouss_mini_ws are reflected on the host OS and the container.

docker rm tow_board

docker run --name tow_board -v "$(pwd)/tow_board_ws:/tow_board_ws" \
    -it --publish 8080:8080 --user=root \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    --device-cgroup-rule='c 189:* rmw' \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    --network host \
    --workdir="/tow_board_ws"\
    tow_board_img

