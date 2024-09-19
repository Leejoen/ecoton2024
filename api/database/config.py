import toml

cuurent_config = toml.load('settings.toml')


API = cuurent_config['API']
MYSQL = cuurent_config['MYSQL']
JWT = cuurent_config['JWT']
MAIL = cuurent_config['MAIL']
# TEST_DB = cuurent_config['TEST_DB']