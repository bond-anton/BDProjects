from __future__ import division, print_function
import time

from BDProjects.Client import Connector, Client


connector = Connector(config_file_name='config.ini')
client = Client(connector=connector)
client.user_manager.sign_in('administrator', 'admin')
client.user_manager.create_user('john_smith', 'secret_password', 'john.smith@somecorp.com', 'John', 'Smith')
client.user_manager.sign_out()
client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.create_user('jack_black', 'secret_password', 'jack.black@somecorp.com', 'Jack', 'Black')
client.user_manager.sign_out()
client.user_manager.sign_in('administrator', 'admin')
jb_user = client.user_manager.create_user('jack_black', 'secret_password', 'jack.black@somecorp.com', 'Jack', 'Black')
client.user_manager.log_opened_sessions()
time.sleep(3)
client.user_manager.log_signed_in_users()
client.user_manager.logoff_all()

client.user_manager.sign_in('john_smith', 'secret_password')
client.user_manager.sign_out()

client.user_manager.sign_in('administrator', 'admin')
client.user_manager.delete_user(jb_user)
client.user_manager.sign_out()
