from ScientificProjects.Manager import ProjectsManager

pm = ProjectsManager('test.db')
pm.add_user('John', 'Smith', 'john.smith@somecorp.com', 'john_smith', 'secret_password')
pm.sign_in('john_smith', 'secret_password')
pm.sign_in('john_smith', 'secret_password_wrong')
pm.sign_in('john_black', 'secret_password')
