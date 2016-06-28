from __future__ import division, print_function
import time

from ScientificProjects.Client import Client

client = Client(config_file_name='config.ini')

client.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.create_user('Jack', 'Black', 'jack.black@somecorp.com', 'jack_black', 'secret_password')
client.user_manager.log_opened_sessions()
time.sleep(3)
client.user_manager.log_signed_in_users()
client.user_manager.logoff_all()

client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.sign_out()

# client.user_manager.delete_user('john_smith', 'secret_password')
client.user_manager.create_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')

client.user_manager.delete_user('jack_black', 'secret_password')
