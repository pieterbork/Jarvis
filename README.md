# Jarvis
A personal python "text" bot that sends and receives end-to-end encrypted messages.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See installation for notes on how to deploy the project on a live system.

Right now, Jarvis only works with signal phone numbers, using this project: https://gitlab.com/morph027/signal-web-gateway/

### Prerequisites
For Jarvis to work correctly, you will need an extra voip number. Grab a google voice or any SIP number, then take a look here: https://morph027.gitlab.io/signal-web-gateway/installation/docker/ and walk through the configuration instructions to register your number.

Make sure you are able to see sends/receives in the docker logs before you move onto the Installation steps.

### Installing

Jarvis requires the signal gateway to be running and accessible at http://signal:5000 as well as a redis instance located at redis:6379. To accomplish this, docker containers and a docker compose image is available in the [docker/ folder](https://github.com/pieterbork/Jarvis/tree/master/docker)

Deploy in docker

```
git clone https://github.com/pieterbork/Jarvis.git
cd Jarvis/docker
```

You now need to create all of the relevant volume files referenced in the [docker-compose.yml](https://github.com/pieterbork/Jarvis/blob/master/docker/docker-compose.yml). 
1. Create a jarvis.cfg file by editing the [example.cfg](https://github.com/pieterbork/Jarvis/blob/master/example.cfg) and placing it at /data/jarvis/jarvis.cfg. 
2. Create the database file with `touch /data/jarvis/jarvis.db`
3. Edit the signal-web-gateway [config.yml](https://github.com/pieterbork/Jarvis/blob/master/docker/signal-web-gateway/config.yml) to use your VOIP number.

You should now be ready to go...
```
sudo /usr/local/bin/docker-compose up
```

Troubleshoot any configuration issues that may arise, then send a signal message to your VOIP number when everything is workin!

### Commands

```
hello
help
ping
get pug
get cat
get joke
set alias <alias>
```

## Issues

Currently, textsecure has multiple references to github.com/agl/ed25519 which no longer exists. I've mirrored the project here: https://github.com/pieterbork/ed25519 and use my own version of textsecure here: https://github.com/pieterbork/textsecure to publish all messages to redis so Jarvis can retrieve them. This isn't really an issue, but something I want to change eventually once they update go references to the new repo for ed25519: https://github.com/golang/crypto/tree/master/ed25519.

## Contributing

Pull requests welcome

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Thanks to https://github.com/signal-golang for the textsecure project
* Thanks to https://gitlab.com/morph027 for the signal-web-gateway project
