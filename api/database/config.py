from configparser import ConfigParser
import toml


# config_with_global = ConfigParser()
# config_with_global.read('settings.ini')

# cuurent_config = toml.load('test_settings.toml')
cuurent_config = toml.load('settings.toml')


API = cuurent_config['API']
MYSQL = cuurent_config['MYSQL']
JWT = cuurent_config['JWT']
TEST_DB = cuurent_config['TEST_DB']