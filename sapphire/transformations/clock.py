""" Time transformations

This handkes all the wibbly wobbly timey wimey stuff.
Such as easy conversions between different time systems.
Supported systems: GPS, UTC, GMST, LST, JD and MJD.

Formulae from:

Duffett-Smith1990
'Astronomy with your personal computer'
ISBN 0-521-38995-X

USNO
'Computing Greenwich Apparent Sidereal Time'
http://aa.usno.navy.mil/faq/docs/GAST.php

Adrian Price-Whelan
apwlib.convert
https://github.com/adrn/apwlib

"""
from time import strptime
import datetime
import math
import calendar

from . import base, angles


def time_to_decimal(time):
    """Converts a time or datetime object into decimal time

    :param time: datetime.time or datetime.datetime object
    :returns: decimal number representing the input time

    """
    return (time.hour + time.minute / 60. + time.second / 3600. +
            time.microsecond / 3600000000.)


def decimal_to_time(hours):
    """Converts decimal time to a time object

    :param hours: datetime.time or datetime.datetime object
    :returns: decimal number representing the input time

    """
    hours, minutes, seconds = base.decimal_to_sexagesimal(hours)
    seconds_frac, seconds = math.modf(seconds)
    seconds = int(seconds)
    microseconds = int(seconds_frac * 1e6)

    return datetime.time(hours, minutes, seconds, microseconds)


def date_to_juliandate(year, month, day):
    """Convert year, month, and day to a Julian Date

    Julian Date is the number of days since noon on January 1, 4713 B.C.
    So the returned date will end in .5 because the date refers to midnight.

    :param year: A Gregorian year (B.C. years are negative)
    :param month: A Gregorian month (1-12)
    :param day: A Gregorian day (1-31)
    :returns: The Julian Date for the given year, month, and day

    """
    year1 = year
    month1 = month

    if year1 < 0:
        year1 += 1
    if month in [1, 2]:
        year1 -= 1
        month1 = month + 12

    if year1 > 1582 or (year1 == 1582 and month >= 10 and day >= 15):
        A = int(year1 / 100)
        B = 2 - A + int(A / 4)
    else:
        B = 0

    if year1 < 0:
        C = int((365.25 * year1) - 0.75)
    else:
        C = int(365.25 * year1)

    D = int(30.6001 * (month1 + 1))

    return B + C + D + day + 1720994.5


def datetime_to_juliandate(dt):
    """Convert a datetime object in UTC to a Julian Date

    :param dt: datetime object
    :returns: The Julian Date for the given datetime object

    """
    A = date_to_juliandate(dt.year, dt.month, dt.day)
    B = time_to_decimal(dt.time()) / 24.
    return A + B


def juliandate_to_modifiedjd(juliandate):
    """Convert a Julian Date to a Modified Julian Date

    :param juliandate: a Julian Date
    :returns: the Modified Julian Date

    """
    return juliandate - 2400000.5


def modifiedjd_to_juliandate(modifiedjd):
    """Convert a Modified Julian Date to Julian Date

    :param modifiedjf: a Modified Julian Date
    :returns: Julian Date

    """
    return modifiedjd + 2400000.5


def datetime_modifiedjd(dt):
    """Convert a datetime object in UTC to a Modified Julian Date

    :param dt: datetime object
    :returns: the Modified Julian Date

    """
    jd = datetime_to_juliandate(dt)
    return juliandate_to_modifiedjd(jd)


def juliandate_to_gmst(juliandate):
    """Convert a datetime object in UTC time to Greenwich Mean Sidereal Time

    :param juliandate: Julian Date
    :return: decimal hours in GMST

    """
    jd0 = int(juliandate - .5) + .5  # Julian Date of previous midnight
    h = (juliandate - jd0) * 24.  # Hours since mightnight
    # Days since J2000 (Julian Date 2451545.)
    d0 = jd0 - 2451545.
    d = juliandate - 2451545.
    t = d / 36525.  # Centuries since J2000

    gmst = (6.697374558 + 0.06570982441908 * d0 + 1.00273790935 * h +
            0.000026 * t * t)

    return gmst % 24.


def utc_to_gmst(dt):
    """Convert a datetime object in UTC time to Greenwich Mean Sidereal Time

    :param dt: datetime object in UTC time
    :return: decimal hours in GMST

    """
    jd = datetime_to_juliandate(dt)

    return juliandate_to_gmst(jd)


def gmst_to_utc(dt):
    """Convert datetime object in Greenwich Mean Sidereal Time to UTC

    Note: this requires a datetime object, not just the decimal hours.

    :param dt: datetime object in GMST time
    :return: datetime object in UTC

    """
    jd = date_to_juliandate(dt.year, dt.month, dt.day)

    d = jd - 2451545.
    t = d / 36525.
    t0 = 6.697374558 + (2400.051336 * t) + (0.000025862 * t * t)
    t0 %= 24

    GST = (time_to_decimal(dt.time()) - t0) % 24
    UT = GST * 0.9972695663

    time = decimal_to_time(hours)

    return dt.replace(hour=time.hour, minute=time.minute, second=time.seconds,
                      microsecond=time.microsecond)


def juliandate_to_utc(juliandate):
    """Convert Julian Date to datetime object in UTC

    :param juliandate: a Julian Date
    :returns: datetime object in UTC time

    """
    juliandate += .5
    jd_frac, jd_int = math.modf(juliandate)

    if jd_int > 2299160:
        A = int((jd_int - 1867216.25) / 36524.25)
        B = jd_int + 1 + A - int(A / 4)
    else:
        B = jd_int

    C = B + 1524
    D = int((C - 122.1) / 365.25)
    E = int(365.25 * D)
    G = int((C - E) / 30.6001)

    day = C - E + jd_frac - int(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
    month = int(month)

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715 # year
    year = int(year)

    day_frac, day = math.modf(day)

    day = int(day)
    date = datetime.date(year, month, day)
    hours = day_frac * 24 # fractional part of day * 24 hours

    time = decimal_to_time(hours)

    return datetime.datetime.combine(date, time)


def modifiedjd_to_utc(modifiedjd):
    """Convert a Modified Julian Date to datetime object in UTC

    :param juliandate: a Modified Julian Date
    :returns: datetime object in UTC time

    """
    juliandate = modifiedjd_to_juliandate(modifiedjd)
    return juliandate_to_utc(juliandate)


def gmst_to_lst(hours, longitude):
    """Convert Greenwich Mean Sidereal Time to Local Sidereal Time

    :param hours: decimal hours in GMST
    :param longitude: location in degrees, E positive
    :returns: decimal hours in LST

    """
    longitude_time = angles.degrees_to_hours(longitude)
    lst = hours + longitude_time
    lst %= 24

    return lst


def lst_to_gmst(hours, longitude):
    """Convert Local Sidereal Time to Greenwich Mean Sidereal Time

    :param hours: decimal hours in LST
    :param longitude: location in degrees, E positive
    :returns: decimal hours in GMST

    """
    longitude_time = angles.degrees_to_hours(longitude)
    gmst = hours - longitude_time
    gmst %= 24

    return gmst


def utc_to_lst(dt, longitude):
    """Convert UTC to Local Sidereal Time

    :param dt: datetime object in UTC
    :param longitude: location in degrees, E positive
    :returns: decimal hours in LST

    """
    gmst = utc_to_gmst(dt)

    return gmst_to_lst(gmst, longitude)


def gps_to_utc(timestamp):
    """Convert GPS time to UTC

    :param timestamp: GPS timestamp in seconds.

    """
    if timestamp < gps_from_string('January 1, 1999'):
        raise Exception("Dates before January 1, 1999 not implemented!")
    elif timestamp < gps_from_string('January 1, 2006'):
        return timestamp - 13
    elif timestamp < gps_from_string('January 1, 2009'):
        return timestamp - 14
    elif timestamp < gps_from_string('July 1, 2012'):
        return timestamp - 15
    else:
        return timestamp - 16


def utc_to_gps(timestamp):
    """Convert UTC to GPS time

    :param timestamp: UTC timestamp in seconds.

    """
    if timestamp < utc_from_string('January 1, 1999'):
        raise Exception("Dates before January 1, 1999 not implemented!")
    elif timestamp < utc_from_string('January 1, 2006'):
        return timestamp + 13
    elif timestamp < utc_from_string('January 1, 2009'):
        return timestamp + 14
    elif timestamp < utc_from_string('July 1, 2012'):
        return timestamp + 15
    else:
        return timestamp + 16


def utc_from_string(date):
    """Convert a date string to UTC"""

    t = strptime(date, '%B %d, %Y')
    return calendar.timegm(t)


def gps_from_string(date):
    """Convert a date string to GPS time"""

    t = strptime(date, '%B %d, %Y')
    return utc_to_gps(calendar.timegm(t))


def gps_to_lst(timestamp, longitude):
    """Convert a GPS timestamp to lst

    :param timestamp: GPS timestamp in seconds
    :param longitude: location in degrees, E positive
    :returns: decimal hours in LST

    """

    utc_timestamp = gps_to_utc(timestamp)
    utc = datetime.datetime.utcfromtimestamp(utc_timestamp)
    return utc_to_lst(utc, longitude)