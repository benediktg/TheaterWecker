# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytz
from celery import shared_task
from celery.schedules import crontab
from celery.task.base import periodic_task
import datetime
import re
import requests
from bs4 import BeautifulSoup

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now, make_aware

from app.models import UserEmail, Performance, Institution, Category, City, Location

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def send_verify_email(email, scheme, host, count):
    try:
        user_email = UserEmail.objects.get(email=email)
        user_email.mail("Willkommen beim TheaterWecker", render_to_string('email/welcome.email', {
            'verification_link': "%s://%s%s" % (scheme, host, reverse('app:verify', kwargs={
                'key': user_email.verification_key
            }))

        }))
    except UserEmail.DoesNotExist as e:
        logger.error('User does not exist', exc_info=True)
        return
    except Exception as e:
        logger.error('Sending email failed', exc_info=True)
        if count > 9:
            logger.error('Sending email failed after 10th retry', exc_info=True)
            return
        send_verify_email.apply_async((email, scheme, host, count + 1), countdown=(2 ** count) * 60)


@periodic_task(run_every=(crontab(hour="4", minute="33", day_of_week="*")))
def passed_performance_cleanup():
    logger.info('cleanup_performances has run')
    Performance.objects.filter(begin__lt=now()).delete()


URL = "http://www.theater-chemnitz.de/spielplan/gesamtspielplan"
time_location_re = re.compile("(?P<hour>\d{2}):(?P<minutes>\d{2})(\s*Uhr\s*)(?P<location>[\w\s]*)")
calendar_months = [
    '',
    'januar',
    'februar',
    'marz',
    'april',
    'mai',
    'juni',
    'juli',
    'august',
    'september',
    'oktober',
    'november',
    'dezember'
]

def get_plays(year, month):
    plan = requests.get(URL, params={
        "month": calendar_months[month],
        "year": year,
        "tip": 1,
    })
    if plan.status_code != 200:
        logger.error('got non-200 return code while scraping', exc_info=True)
        return []
    soup = BeautifulSoup(plan.text.replace('&nbsp;', ' '), "lxml")
    block_tops = soup.find_all("div", class_="block_top")
    plays = []
    for block_top in block_tops:
        date = block_top.find("div", class_="pr_box_data_01")
        if date:
            day = int(date.get_text())
            infos = block_top.find_all("div", class_="pr_box_info")
            for info in infos:
                play = {
                    "month": month,
                    "day": day,
                    "year": year
                }
                time_location_raw = info.find(class_="news_box_in_left_in_top")
                m = time_location_re.match(time_location_raw.get_text())
                play["hour"] = int(m.group("hour"))
                play["minutes"] = int(m.group("minutes"))
                play["location"] = m.group("location")
                # Gastspiel, Premiere etc.
                special_raw = info.find("span", class_="pr_red")
                if special_raw:
                    special = special_raw.get_text()
                    if special in ["Gastspiel"]:  # Ausnahmen
                        continue
                category_raw = info.find(class_="pr_box_content_right_table_top")
                if category_raw:
                    category = category_raw.get_text()
                    if category in ["Theaternahes Rahmenprogramm"]:
                        category = "Sonstiges"
                    play["category"] = category
                title_raw = info.find(class_="mini_title_link_b")
                if title_raw:
                    play["title"] = title_raw.get_text()
                else:
                    continue
                desciption_raw = info.find(class_="news_box_descript")
                if desciption_raw:
                    play["description"] = desciption_raw.get_text()
                tickets_raw = info.find("a", class_="karten")
                play["tickets"] = tickets_raw
                plays.append(play)
    if len(plays) == 0:
        logger.error('could not find a single play while scraping', exc_info=True)
    return plays

@periodic_task(run_every=(crontab(hour="*", minute="4", day_of_week="*")))
def scrape_performances_in_chemnitz():
    logger.info('run it')
    today = datetime.date.today()
    plays = get_plays(today.year, today.month)
    if today.month + 1 == 13:
        plays.extend(get_plays(today.year + 1, 1))
    else:
        plays.extend(get_plays(today.year, today.month + 1))

    city, _ = City.objects.get_or_create(name='Chemnitz')
    institution, _ = Institution.objects.get_or_create(name='Theater', city=city)

    for play in plays:
        location, _ = Location.objects.get_or_create(name=play.get('location', "Theater Chemnitz"), institution=institution)
        category, _ = Category.objects.get_or_create(name=play.get('category', 'Sonstiges'), institution=institution)
        begin = make_aware(datetime.datetime(play['year'], play['month'], play['day'], play['hour'], play['minutes']), pytz.timezone('Europe/Berlin'))

        data = {
            "title": play.get('title'),
            "location": location,
            "category": category,
            "begin": begin.isoformat(),
            "description": play.get('description', ''),
        }

        if not play['tickets']:
            try:
                performance = Performance.objects.get(
                   **data
                )
            except Performance.DoesNotExist:
                pass
            else:
                logger.warning('performance deleted', exc_info=True)
                performance.delete()
        else:
            performance, created = Performance.objects.get_or_create(
                **data
            )
            if created:
                logger.warning('performance created', exc_info=True)