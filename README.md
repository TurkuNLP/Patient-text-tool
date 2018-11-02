# Patient text tool
## Installing the text tool.

The easiest way to install is to first install docker (Ubuntu):
```
sudo apt install docker.io
```
Add a user to the docker group with:
```
sudo usermod -a -G docker <user>
```
Relogin might be required.

Then pull the image from the public repository:
```
docker pull haamis/patient_text_tool
```

#### Building the docker image manually from the sources.
```
docker build -t patient_text_tool .
```
`-t` gives the result image a (human-friendly) name.
Building the image takes several minutes due to the large amount of dependencies.

## Running the text tool.

You can start the docker container with the command:
```
docker run -d -p 127.0.0.1:3000:3000/tcp -p 127.0.0.1:5000:5000/tcp -p 127.0.0.1:8983:8983/tcp --name patient_text_tool haamis/patient_text_tool
```

`-p` publishes given port to the host interfaces. With 127.0.0.1 these ports are only visible to localhost. It is possible to change the port on the host's side by changing the first port number, e.g. if you wanted the web server to be accessible on port 80: `-p 127.0.0.1:80:3000/tcp`.
`--name` specifies a name for the running container.
The last argument is the name of the docker image to run.

#### Managing the docker container

You can stop or start the container with the commands `docker stop patient_text_tool` and `docker start patient_text_tool`. The start command is particularly useful for recovering from a reboot.

## Indexing files to the Solr server running on the container.
Once the container is running:
```
docker exec -i patient_text_tool ./index.py < <csv_file>
```
where `<csv_file>` is a csv dump from a database. The command does not print anything until it is completed. If you see a list of numbers when it quits, it has worked. The `-i` option is necessary for STDIN to the container to work.

## Running the software without docker.

This involves installing all the necessary dependencies (java, python3, ruby, see the Dockerfile) and starting up the servers manually. Possible, but not recommended.

## License
[Apache 2](https://www.apache.org/licenses/LICENSE-2.0)
