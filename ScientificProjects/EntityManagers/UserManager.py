from __future__ import division, print_function

from sqlalchemy.exc import IntegrityError

from ScientificProjects.Entities.Users import User
from ScientificProjects.EntityManagers import EntityManager


class UserManager(EntityManager):

    def __init__(self, engine):
        self.user = None
        super(UserManager, self).__init__(engine)

    def create_user(self, name_first, name_last, email, login, password):
        user = User(name_first=str(name_first), name_last=str(name_last),
                    email=str(email), login=str(login), password=str(password))
        try:
            self.session.add(user)
            self.session.commit()
            print('User %s successfully created' % user.login)
            return user
        except IntegrityError as e:
            print('User with provided login/email is already registered')
            self.session.rollback()
            return self.session.query(User).filter(User.login == str(login)).one()

    def sign_in(self, login, password):
        user = self.session.query(User).filter(User.login == str(login)).all()
        if user:
            user = user[0]
            if user.password == str(password):
                self.user = user
                self.user.signed_in = True
                self.session.commit()
                print('%s signed in' % self.user.login)
                print('Welcome back, %s %s' % (user.name_first, user.name_last))
            else:
                print('Incorrect username/password')
        else:
            print('Incorrect username/password')

    def sign_out(self):
        if self.signed_in():
            self.user.signed_in = False
            self.session.commit()
            print('%s signed out' % self.user.login)
            self.user = None

    def signed_in(self):
        if isinstance(self.user, User):
            if self.user.signed_in:
                return True
        return False

    def signed_in_users(self):
        users = self.session.query(User).filter(User.signed_in == True).all()
        signed_in_users = {}
        for user in users:
            signed_in_users[user.login] = {'full name': '%s %s' % (user.name_first, user.name_last),
                                           'email': user.email}
        return signed_in_users

    def logoff_all(self):
        users = self.session.query(User).filter(User.signed_in == True).all()
        for user in users:
            user.signed_in = False
            self.session.commit()
