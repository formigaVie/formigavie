#!/usr/bin/env python
import os
import jinja2
import webapp2
import random
import datetime
import model
import string # import for PWDHandler
import json # import for WeatherHandler
#from random import * # import for PWDHandler
from google.appengine.api import users # import for Google Login
from google.appengine.api import urlfetch # import for WeatherHandler

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")


class BlogHandler(BaseHandler):
    def get(self):
        current_datetime2 = datetime.datetime.now()
        readable_date2 = current_datetime2.strftime("%Y-%m-%d %H:%M")
        return self.render_template("blog.html", params={"site_date2": readable_date2})


class ContactHandler(BaseHandler):
    def get(self):
        current_datetime4 = datetime.datetime.now()
        readable_date4 = current_datetime4.strftime("%Y-%m-%d %H:%M")
        return self.render_template("contact.html",params={"site_date4": readable_date4})


MY_HISTORY=[]

readabledate = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


class LottoHandler(BaseHandler):
    def get(self):
        global MY_HISTORY
        current_datetime = datetime.datetime.now()
        readable_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        my_lotto = random.sample(range(0,45),6)
        # append date and my_lotto to MY_HISTORY
        MY_HISTORY.append( (readable_date,my_lotto) )
        return self.render_template("lotto.html", params={"mylotto": my_lotto,
                                                          "site_date": readable_date,
                                                          "site_history": MY_HISTORY})


class CGHandler(BaseHandler):
    def get(self):
            return self.render_template("capitalsgame.html")

    def post(self):
            has_guessed = True
            guess = self.request.get("guess")

            # secretnumber = random.sample((0,5),1)
            #  "site_date": readable_date,


class SNGHandler(BaseHandler):
    def get(self):
        return self.render_template("sng.html")

    def post(self):
        has_guessed = True
        guess = self.request.get("guess")
        # secretnumber = random.sample((0,5),1)
        secretnumber = 4
        number = int(guess or 0)
        # wenn guess keinen Wert hat oder leer ist
        is_guessed = secretnumber == number
        return self.render_template("sng.html", params={"is_guessed": is_guessed,
                                                        "has_guessed": has_guessed})


class RBlHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        messages = model.Message.query(model.Message.deleted == False).fetch()
        messages = sorted(messages, key=lambda x: x.created)[::-1]
        if user:
            logged_in = True
            logout_url = users.create_logout_url("/realblog")
            params = {"logged_in": logged_in, "logout_url":logout_url, "user": user, "messages": messages}
        else:
            logged_in = False
            login_url = users.create_login_url("/realblog")
            params = {"logged_in": logged_in, "login_url": login_url, "user": user, "messages": messages}
        self.render_template("realblog.html", params=params)

    def post(self):
        uname = self.request.get("username")
        uname = str(uname or "Anonymous")
        message_t = self.request.get("message_text")
        message_t = message_t.replace("<", "&lt")
        message_t = message_t.replace(">", "&gt")
        email_t = self.request.get("useremail")
        if email_t:
            pass
        else:
            email_t = users.get_current_user().email()
        message = model.Message(message_text=message_t, name=uname, email_text=email_t)
        message.put()
        return self.redirect_to("realblog")


class EditMessageHandler(BaseHandler):
    def get(self, message_id):
        message = model.Message.get_by_id(int(message_id))
        return self.render_template("edit_message.html", params={"message": message})

    def post(self, message_id):
        message = model.Message.get_by_id(int(message_id))
        message.message_text=self.request.get("message_text")
        message.message_name=self.request.get("username")
        message.put()
        return self.redirect_to("realblog")


class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        message = model.Message.get_by_id(int(message_id))
        return self.render_template("delete_message.html", params={"message": message})

    def post(self, message_id):
        message = model.Message.get_by_id(int(message_id))
        #message.key.delete() #for real delete
        fdelete = self.request.get("fdel")
        delete = self.request.get("del")
        undo = self.request.get("und")
        if fdelete == "fd":
            message.deleted=True
            message.put()
        elif undo == "un":
            message.deleted=False
            message.put()
        elif delete == "de":
            message.key.delete()

        return self.redirect_to("realblog")


class FDeleteMessageHandler(BaseHandler):
    def get(self):
        messages = model.Message.query(model.Message.deleted == True).fetch()
        # additional line for sorting the imported messages
        messages = sorted(messages, key=lambda x: x.created)[::-1]
        return self.render_template("fake_del.html", params={"messages": messages})
    #def get(self,message_id):
    #    messages = model.Message.query(model.Message.deleted == True).fetch()
    #    # additional line for sorting the imported messages
    #    messages = sorted(messages, key=lambda x: x.created)[::-1]
    #    return self.render_template("fake_del.html", params={"messages": messages})

    #def post(self):
    #    pass
        #message = model.Message.get_by_id(int(message_id))
        #full_del = self.request.get("complete_del_btn")
        #back = self.request.get("undo_btn")
        #if full_del:
        #    message.key.delete()
        #    message.put()
        #elif back:
        #    message.deleted = False
        #    message.put()
        #else:
        #    pass
        #return self.redirect_to("realblog")


class CalcHandler(BaseHandler):
    def get(self):
        return self.render_template("calculator.html")

    def post(self):
        has_guessed = True
        x = self.request.get("x")
        ops = self.request.get("operation_symbol")
        y = self.request.get("y")

        a = float(x or 0)
        b = float(y or 0)

        if ops == "+" or ops == "-" or ops == "*" or ops == "/":
            is_ok = True
            if ops == "+":
                solution = a + b
            elif ops == "-":
                solution = a - b
            elif ops == "/":
                #if b == 0:
                #    # additional entry if divisor is 0
                #    print "Division by Zero"
                #else:
                solution = a / b
            elif ops == "*":
                solution = a * b
        else:
            is_ok = False

        return self.render_template("calculator.html", params={"opsy": is_ok,
                                                               "sols": solution})


class UnCoHandler(BaseHandler):
    def get(self):
        return self.render_template("unitconverter.html")

    def post(self):
        hasguessed = True
        initstate = self.request.get("length")
        DIGITS = 2
        lconv = round(float(initstate or 0)/ 1.61, DIGITS)
        return self.render_template("unitconverter.html", params={"has_guessed": hasguessed,
                                                                  "convers": lconv,
                                                                  "initst": initstate})


class PwdHandler(BaseHandler):
    def get(self):
        return self.render_template("password.html")

    def post(self):
        hasguessed = True
        vers = "V0.2"
        min_char = 8
        max_char = 12
        allchar = string.ascii_letters + string.punctuation + string.digits
        allchar2 = string.ascii_letters + string.digits
        password = "".join(random.choice(allchar) for x in range(random.randint(min_char, max_char)))
        length1=len(password)
        password2 = "".join(random.choice(allchar2) for x in range(random.randint(min_char, max_char)))
        length2=len(password2)
        readabledate = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        return self.render_template("password.html", params={"pwd": password,
                                                             "len1": length1,
                                                             "pwd2": password2,
                                                             "len2": length2,
                                                             "ver": vers,
                                                             "radate": readabledate,
                                                   "has_guessed": hasguessed})


class WeatherHandler(BaseHandler):
        def get(self):
            url = "http://api.openweathermap.org/data/2.5/weather?q=Vienna,at&units=metric&appid=35fe998feccf4baf99b049191dccc3ac"
            url2 = "http://api.openweathermap.org/data/2.5/weather?q=Denpasar&units=metric&appid=35fe998feccf4baf99b049191dccc3ac"
            result = urlfetch.fetch(url)
            result2 = urlfetch.fetch(url2)
            weather_info = json.loads(result.content)
            weather_info["sys"]["sunrise"]=datetime.datetime.fromtimestamp(weather_info["sys"]["sunrise"])
            weather_info["sys"]["sunset"]=datetime.datetime.fromtimestamp(weather_info["sys"]["sunset"])
            weather_info2 = json.loads(result2.content)
            weather_info2["sys"]["sunrise"]=datetime.datetime.fromtimestamp(weather_info2["sys"]["sunrise"])
            weather_info2["sys"]["sunset"]=datetime.datetime.fromtimestamp(weather_info2["sys"]["sunset"])
            current_datetime = datetime.datetime.now()
            readable_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            params = {"weather_info": weather_info,
                      "weather_info2": weather_info2,
                      "current_date": readable_date}
            return self.render_template("weather.html", params)


def get_crypto_info(coin):
    base_url = "https://api.coinmarketcap.com/v1/ticker/{}/?convert=EUR".format(coin)
    result = urlfetch.fetch(base_url)
    data = json.loads(result.content)[0]
    data["last_updated"] = datetime.datetime.fromtimestamp(float(data["last_updated"]))
    return data


class CryptoHandler(BaseHandler):
        def get(self):
            coins = ["bitcoin", "ethereum", "litecoin"]
            info_c = [get_crypto_info(coin) for coin in coins]
            current_datetime = datetime.datetime.now()
            readable_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            params = {"infoc": info_c,
                      "current_date": readable_date}
            return self.render_template("crypto.html", params)


TODO = []


class TodoHandler(BaseHandler):
        def get(self):
            return self.render_template("todo.html")

        def post(self):
            global readabledate
            global TODO
            has_guessed = True
            task = self.request.get("Todo")
            TODO.append( (readabledate, task) )
            return self.render_template("todo.html", params={"todotask": task,
                                                             "guessed": has_guessed,
                                                             "readabledate": readabledate,
                                                             "sitehistory": TODO })

# for first test this Route was established
#class LoginHandler(BaseHandler):
#    def get(self):
#        user = users.get_current_user()
#        if user:
#            logged_in = True
#            logout_url = users.create_logout_url("/")
#            params = {"logged_in": logged_in, "logout_url": logout_url, "user": user}
#        else:
#            logged_in = False
#            login_url = users.create_login_url("/")
#            params = {"logged_in": logged_in, "login_url": login_url, "user": user}
#        self.render_template("login.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/blog', BlogHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/lotto', LottoHandler),
    webapp2.Route('/capital', CGHandler),
    webapp2.Route('/sng',SNGHandler),
    webapp2.Route('/realblog', RBlHandler, name="realblog"),
    webapp2.Route('/calculator', CalcHandler),
    webapp2.Route('/unitconverter', UnCoHandler),
    webapp2.Route('/password', PwdHandler),
    webapp2.Route('/message/<message_id:\d+>/edit', EditMessageHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),
#    webapp2.Route('/message/<message_id:\d+>/fakedelete',FDeleteMessageHandler),
    webapp2.Route('/fakedelete',FDeleteMessageHandler),
    webapp2.Route('/weather',WeatherHandler),
    webapp2.Route('/crypto',CryptoHandler),
    webapp2.Route('/todo',TodoHandler),
    # for first test this Route was established
    # webapp2.Route('/logintest', LoginHandler, name="logintest"),
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='0.0.0.0', port='8090')


if __name__ == '__main__':
    main()