import webapp2
import jinja2
import os
import logging
import time

from google.appengine.ext import ndb
from google.appengine.api import users

class Person(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    gender = ndb.StringProperty()
    college = ndb.StringProperty()
    year = ndb.StringProperty()
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    bio = ndb.StringProperty()
    sleep = ndb.StringProperty()
    smoke = ndb.StringProperty()
    hobbies = ndb.StringProperty()
    photo = ndb.BlobProperty()

class Like(ndb.Model):
    liker_key = ndb.KeyProperty()
    liked_key = ndb.KeyProperty()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        # 1. Read the request
        current_user = users.get_current_user()
        # 2. Read/write from the database
        people = Person.query().fetch()
        if current_user:
            current_email = current_user.email()
            current_person = Person.query().filter(Person.email == current_email).get()
            if current_person:
                self.redirect("/potentialroomies")
        else:
            current_person = None
        # 3. Render the response
        logout_url = users.create_logout_url("/")

        if current_person:
            login_url = users.create_login_url("/")
        else:
            login_url = users.create_login_url("/")

        templateVars = {
            "people" : people,
            "current_user" : current_user,
            "login_url" : login_url,
            "logout_url" : logout_url,
            "current_person" : current_person,
        }
        template = env.get_template("templates/home.html")
        self.response.write(template.render(templateVars))

class ProfilePage(webapp2.RequestHandler):#has protection against the back button error (line 69-70)
    def get(self):
        # 1. Read the request
        urlsafe_profile_key = self.request.get("key") #get from url
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return
        else:
            current_person = Person.query().filter(Person.email == current_user.email()).get()
        # 2. Read/write from the database
        key = ndb.Key(urlsafe=urlsafe_profile_key)# from url to key
        viewed_person = key.get()#from key to person object

        is_my_profile = current_user and current_user.email() == viewed_person.email
        logout_url = users.create_logout_url("/")

        current_person_likes = Like.query().filter(Like.liker_key == current_person.key).fetch()
        likes_current_person = Like.query().filter(Like.liked_key == current_person.key).fetch()
        mutual_likes = current_person_likes and likes_current_person

        people_person_likes= []
        people_likes_person = []
        matches = []

        for like in current_person_likes:
            liked = Person.query().filter(Person.key == like.liked_key).get()
            if liked and not liked in people_person_likes:
                people_person_likes.append(liked)

        for like in likes_current_person:
            liker = Person.query().filter(Person.key == like.liker_key).get()
            if liker and not liker in people_likes_person:
                people_likes_person.append(liker)

        for like in current_person_likes:
            likes = Like.query().filter(Like.liker_key == like.liked_key).filter(Like.liked_key == current_person.key).fetch()
            if likes:
                mutual = Person.query().filter(Person.key == like.liked_key).get()
                if not mutual in matches:
                    matches.append(mutual)
        # 3. Render the response
        templateVars = {
            "current_person" : current_person,
            "people_person_likes" : people_person_likes,
            "people_likes_person" : people_likes_person,
            "person" : viewed_person,
            "is_my_profile" : is_my_profile,
            "logout_url" : logout_url,
            "matches" : matches,
        }
        template = env.get_template("templates/profile.html")
        self.response.write(template.render(templateVars))

    def post(self):
        #1
        current_user = users.get_current_user()
        current_person = Person.query().filter(Person.email == current_user.email()).get()

        viewed_profile_key = self.request.get("viewed_profile_key") #this is the urlsafe key getting returned
        key = ndb.Key(urlsafe=viewed_profile_key)
        viewed_profile = key.get()
        #2
        like = Like(liker_key = current_person.key, liked_key = viewed_profile.key)
        like.put()
        #3
        time.sleep(2)
        self.redirect("/profile?key=" + viewed_profile.key.urlsafe())

class CreateHandler(webapp2.RequestHandler):
    def post(self):
        # 1. Read the request
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return

        name = self.request.get("name")
        gender = self.request.get("gender")
        college = self.request.get("college")
        year = self.request.get("year")
        city = self.request.get("city")
        state = self.request.get("state")
        bio = self.request.get("bio")
        sleep = self.request.get("sleep")
        smoke = self.request.get("smoke")
        hobbies = self.request.get("hobbies")
        current_user = users.get_current_user()
        email = current_user.email()
        # 2. Read/write from the database
        person = Person(name=name, gender=gender, college=college, year=year, city=city, state=state, bio=bio, email=email, sleep=sleep, smoke=smoke, hobbies=hobbies)
        person.put()
        # 3. Render the response
        time.sleep(2)#gives it time to render
        self.redirect("/potentialroomies")

class EditHandler(webapp2.RequestHandler):
    def post(self):
        current_user = users.get_current_user()
        current_person = Person.query().filter(Person.email == current_user.email()).get()
        person = Person.query().filter(Person.email == current_user.email()).get()
        name = self.request.get("name")
        gender = self.request.get("gender")
        college = self.request.get("college")
        year = self.request.get("year")
        city = self.request.get("city")
        state = self.request.get("state")
        bio = self.request.get("bio")
        sleep = self.request.get("sleep")
        smoke = self.request.get("smoke")
        hobbies = self.request.get("hobbies")

        person.name = name
        person.gender = gender
        person.college = college
        person.year = year
        person.city = city
        person.state = state
        person.bio = bio
        person.sleep = sleep
        person.smoke = smoke
        person.hobbies = hobbies
        person.put()
        time.sleep(2)
        self.redirect("/profile?key=" + current_person.key.urlsafe())

class PhotoUploadHandler(webapp2.RequestHandler):
    def post(self):
        image = self.request.get("image")
        current_user = users.get_current_user()
        current_person = Person.query().filter(Person.email == current_user.email()).get()
        current_person.photo = image
        current_person.put()
        time.sleep(2)
        self.redirect("/profile?key=" + current_person.key.urlsafe()) #current person is the person from database, cannot get key from current user

class PhotoHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get("key")
        key = ndb.Key(urlsafe=urlsafe_key)
        person = key.get()
        self.response.headers["Content-Type"] = "image/jpg"
        if not person.photo:
            f=open("images/defaultpic.jpg","r")
            self.response.write(f.read())
            f.close()
        else:
            self.response.write(person.photo)

class PotentialRoomies(webapp2.RequestHandler):
    def get(self):
        #1
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return
        else:
            current_person = Person.query().filter(Person.email == current_user.email()).get()
        #2
        people = Person.query()

        if self.request.get("college_filter") == "on":
            people = people.filter(Person.college == current_person.college)
        if self.request.get("year_filter") == "on":
            people = people.filter(Person.year == current_person.year)
        if self.request.get("gender_filter") == "on":
            if current_person.gender != "Other":
                people = people.filter(Person.gender == current_person.gender)
        if self.request.get("city_filter") == "on":
            people = people.filter(Person.city == current_person.city)
        if self.request.get("state_filter") == "on":
            people = people.filter(Person.state == current_person.state)
        if self.request.get("sleep_filter") == "on":
            people = people.filter(Person.sleep == current_person.sleep)
        if self.request.get("smoke_filter") == "on":
            people = people.filter(Person.smoke == current_person.smoke)
        if self.request.get("hobbies_filter") == "on":
            people = people.filter(Person.hobbies == current_person.hobbies)

        people = people.fetch()
        #3
        current_person_likes = Like.query().filter(Like.liker_key == current_person.key).fetch()
        likes_current_person = Like.query().filter(Like.liked_key == current_person.key).fetch()
        mutual_likes = current_person_likes and likes_current_person

        people_person_likes= []
        people_likes_person = []
        matches = []

        for like in current_person_likes:
            liked = Person.query().filter(Person.key == like.liked_key).get()
            if liked and not liked in people_person_likes:
                people_person_likes.append(liked)

        for like in likes_current_person:
            liker = Person.query().filter(Person.key == like.liker_key).get()
            if liker and not liker in people_likes_person:
                people_likes_person.append(liker)

        for like in current_person_likes:
            likes = Like.query().filter(Like.liker_key == like.liked_key).filter(Like.liked_key == current_person.key).fetch()
            if likes:
                mutual = Person.query().filter(Person.key == like.liked_key).get()
                if not mutual in matches:
                    matches.append(mutual)
        logout_url = users.create_logout_url("/")

        templateVars = {
            "current_person" : current_person,
            "people" : people,
            "logout_url" : logout_url,
            "people_person_likes" : people_person_likes,
            "people_likes_person" : people_likes_person,
            "matches" : matches,
        }
        template = env.get_template("templates/potentialroomies.html")
        self.response.write(template.render(templateVars))

class MyMatches(webapp2.RequestHandler):
    def get(self):
        #1
        current_user = users.get_current_user()
        if not current_user:
            self.redirect('/')
            return
        else:
            current_person = Person.query().filter(Person.email == current_user.email()).get()
        #2
        current_person_likes = Like.query().filter(Like.liker_key == current_person.key).fetch()
        likes_current_person = Like.query().filter(Like.liked_key == current_person.key).fetch()
        mutual_likes = current_person_likes and likes_current_person

        people_person_likes= []
        people_likes_person = []
        matches = []

        for like in current_person_likes:
            liked = Person.query().filter(Person.key == like.liked_key).get()
            if liked and not liked in people_person_likes:
                people_person_likes.append(liked)

        for like in likes_current_person:
            liker = Person.query().filter(Person.key == like.liker_key).get()
            if liker and not liker in people_likes_person:
                people_likes_person.append(liker)

        for like in current_person_likes:
            likes = Like.query().filter(Like.liker_key == like.liked_key).filter(Like.liked_key == current_person.key).fetch()
            if likes:
                mutual = Person.query().filter(Person.key == like.liked_key).get()
                if not mutual in matches:
                    matches.append(mutual)
        #3
        logout_url = users.create_logout_url("/")
        templateVars = {
            "current_person" : current_person,
            "people_person_likes" : people_person_likes,
            "people_likes_person" : people_likes_person,
            "matches" : matches,
            "logout_url" : logout_url,
        }
        logging.info(matches)
        template = env.get_template("templates/mymatches.html")
        self.response.write(template.render(templateVars))

class About(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        current_person = Person.query().filter(Person.email == current_user.email()).get()
        logout_url = users.create_logout_url("/")
        templateVars = {
            "current_person" : current_person,
            "logout_url" : logout_url,
        }
        template = env.get_template("templates/about.html")
        self.response.write(template.render(templateVars))

app = webapp2.WSGIApplication([
    ("/", MainPage),
    ("/profile", ProfilePage),
    ("/create", CreateHandler),
    ("/edit", EditHandler),
    ("/upload_photo", PhotoUploadHandler),
    ("/photo", PhotoHandler),
    ("/potentialroomies", PotentialRoomies),
    ("/mymatches", MyMatches),
    ("/about", About)
], debug=True)
