#!/usr/bin/env python3

import requests, pickle
from lxml import html
from os import path
from bs4 import BeautifulSoup
from email import *
import random
from threading import Timer
import browser_cookie3

class FormStalker(object):
    def __init__(self):
        self.login_url = "/login"
        self.available_forms_url = "/form"
        self.form1_url = "/select"
        self.form_urls = []
        self.timer_max = 3
        self.timer_cnt = 0
        self.session_requests = requests.session()
        self.cookiejar = browser_cookie3.firefox(domain_name='.com')
        self.from_jar = False
        self.flag = False
        self.mail_content_seat = '''OPEN SEATS!! \n
        /select
        '''
        self.mail_login = '''Robot Filter is ON. Sorry, gonna quit. \n
        '''
        self.mail_subject_seat = 'Seat is available!!'
        self.mail_subject_login = 'Oh No'
        self._stalker()

    def _stalker(self):
        if not self.from_jar:
            self._load_session()
        if not self._check_login():
            pass
        self._get_forms()
        self._check_seats()
        time_to_next = int(random.uniform(5*60,10*60))
        if not self.flag:
            return
            time_to_next = 1.5*60*60
        stalker_timer = Timer(time_to_next, self._stalker)
        stalker_timer.start()

    def _get_forms(self):
        if self.flag:
            if self.from_jar:
                result = self.session_requests.get(self.available_forms_url, cookies=self.cookiejar)
            else:
                result = self.session_requests.get(self.available_forms_url)
            tree = html.fromstring(result.content)
            soup = BeautifulSoup(result.content, 'html.parser')
            self._save_session()
            title = [x.text for x in soup.find_all('div', {'id': '_title'})]
            if len(title) <= 0 or title[0].find("") == -1:
                self.flag = False
                print("session not alive")
            else:
                forms = [1 for x in soup.find_all('div', {'class': '_event'})]
                if len(forms) > 1:
                    self._send_email(''' New form is available. \n Check it out.''', 'New Form!!')
        return self.flag

    def _send_email(self, data, subject_text):
        send_email(data, subject_text)

    def _check_login(self):
        if self.flag:
            if self.from_jar:
                result = self.session_requests.get(self.available_forms_url, cookies=self.cookiejar)
            else:
                result = self.session_requests.get(self.available_forms_url)
            tree = html.fromstring(result.content)
            soup = BeautifulSoup(result.content, 'html.parser')
            title = [x.text for x in soup.find_all('div', {'id': '_title'})]
            print(title)
            if len(title) <= 0 or title[0].find("") == -1:
                self.flag = False
                print("session not alive")
            self._save_session()
        return self.flag

    def _login(self):
        if self.flag == False:
            if self.from_jar:
                result = self.session_requests.get(self.available_forms_url, cookies=self.cookiejar)
            else:
                result = self.session_requests.get(self.available_forms_url)
            tree = html.fromstring(result.text)
            self.authenticity_token = list(set(tree.xpath("//input[@name='fb_csrf']/@value")))[0]
            print(self.authenticity_token)
            self.payload = {
                "id": "",
                "password": "",
                "fb_csrf": self.authenticity_token
            }
            result = self.session_requests.post(
                self.login_url,
                data = self.payload,
                headers = dict(referer=self.login_url)
            )
            self.flag = True
            self._save_session()
        return self.flag

    def _save_session(self):
        with open('form_session', 'wb') as f:
            print(self.cookiejar)
            pickle.dump(self.session_requests.cookies, f)

    def _load_session(self):
        if path.exists('form_session'):
            with open('form_session', 'rb') as f:
                self.session_requests.cookies.update(pickle.load(f))
                self.flag = True
        return self.flag

    def _check_seats(self):
        if self.flag:
            result = self.session_requests.get(self.form1_url)
            tree = html.fromstring(result.content)
            soup = BeautifulSoup(result.content, 'html.parser')
            title = [x.text for x in soup.find_all('div', {'id': '_title'})]
            self._save_session()
            if len(title) <= 0 or title[0].find("") == -1:
                self.flag = False
                return self.flag
            cnt = 0
            for i in soup.find_all('div', {'class': '_item'}):
                cnt += 1
            print(cnt)
            open_seats = []
            full_seats = []
            full_cnt = 0
            open_cnt = 0
            if cnt:
                full_seats = [[x.text for x in i.find_all('div', {'class': '_full'})] for i in soup.find_all('div', {'class': '_item'})]
                open_seats = [[x.text for x in i.find_all('div', {'class': '_open'})] for i in soup.find_all('div', {'class': '_item'})]
            for i in full_seats:
                if len(i):
                    full_cnt += 1
            for i in open_seats:
                if len(i):
                    open_cnt += 1
            if not open_cnt == 0:
                print("sent email!")
                self._send_email(self.mail_content_seat, self.mail_subject_login)
            elif full_cnt == cnt:
                print("All full.")
            else:
                print("some seats are done.")
        return self.flag

bs = FormStalker()
