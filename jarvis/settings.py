PUGME_URL = 'http://pugme.herokuapp.com/random'
CAT_URL = 'http://aws.random.cat/meow'
JOKE_URL = 'https://icanhazdadjoke.com/'

#### Modules and permissions ####
# MODULE_COMMANDS contains all available commands mapped to their permission level. 0=no auth, 1=trusted, 2=admin
MODULE_COMMANDS = {'ping': 0, 'help': 0, 'whoami': 0, 'get': 0, 'set': 2, 'list': 2, 'delete': 2, 'schedule': 2, 'charge': 2, 'bill': 2, 'run': 2}

### Command Module related variables ####
COMMANDS = ['ping', 'help', 'whoami', 'get', 'set', 'list', 'delete', 'run']
GREETINGS = ['hello', 'hi', 'hey', 'hola', 'bonjour']
INTRODUCTIONS = ['my name is', 'im', "i'm"]
STATEMENTS =  ['you are', 'this is', 'we are']
QUESTIONS = ['what is', 'whats', 'do you', 'how do', 'when']
VULGARITIES = ['shutup', 'stfu', 'shut up', 'fuck']
PHONE_REGEX = "^(\+\d{1,2})?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
SCRIPTS = {
        'get_trash_schedule': {'aliases': ['trash', 'recycle', 'compost'], 'args':{'location': '1054 Kane Drive', 'days': 7}},
        'notify_overdue_payments': {'aliases': ['payments'], 'args': {}},
        }


