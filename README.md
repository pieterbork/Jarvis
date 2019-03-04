# Jarvis
A text/email python bot

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See installation for notes on how to deploy the project on a live system.

### Prerequisites
For Jarvis to work correctly, you must create a google voice account as well as an email account (I'm using gmail but should work with other imap servers too). Once you've created these accounts, place the credentials in example.cfg.

### Installing
Run locally

```
git clone https://github.com/pieterbork/Jarvis.git
cd Jarvis
pip install -r requirements.txt
mv example.cfg jarvis.cfg && vi jarvis.cfg #Add your information to jarvis.cfg
python run.py -c jarvis.cfg
```

Run with docker

```
git clone https://github.com/pieterbork/Jarvis.git
cd Jarvis
mv example.cfg jarvis.cfg && vi jarvis.cfg #Add your information to jarvis.cfg
cd docker && sudo docker build -t jarvis:latest .
sudo docker-compuse up -d
```

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

### Issues
Unfortunately, because google voice has no official API, XML Parsing to retrieve sms messages is necessary and is currently done with https://github.com/jaraco/googlevoice. Parsing seems to break whenever a non-utf8 character is included in an sms message and must be deleted before jarvis can continue. 

## Contributing

Pull requests welcome

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Thanks to https://github.com/jaraco/googlevoice for the unofficial API
