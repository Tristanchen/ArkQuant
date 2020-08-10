# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:37:47 2019

@author: python
"""
import numpy as np, datetime, pandas as pd, pytz

MAX_MONTH_RANGE = 23
MAX_WEEK_RANGE = 5


def locate_pos(price, minutes, direction):
    if minutes.min() <= price <= minutes.max():
        try:
            loc = minutes.values().index(price)
        except ValueError:
            idx = np.searchsorted(minutes.values(), price)
            # 当卖出价格大于bid价格才会成交，买入价格低于bid价格才会成交
            # 变相实现了当价格超过范围的时候默认为最高价格 length -1
            loc = idx if direction == 'negative' else idx - 1
            loc = min(loc, len(minutes) - 1)
        return price, minutes.index[loc]


def parse_date_str_series(format_str, tz, date_str_series):
    tz_str = str(tz)
    if tz_str == pytz.utc.zone:

        parsed = pd.to_datetime(
            date_str_series.values,
            format=format_str,
            utc=True,
            errors='coerce',
        )
    else:
        parsed = pd.to_datetime(
            date_str_series.values,
            format=format_str,
            errors='coerce',
        ).tz_localize(tz_str).tz_convert('UTC')
    return parsed


def naive_to_utc(ts):
    """
    Converts a UTC tz-naive timestamp to a tz-aware timestamp.
    """
    # Drop the nanoseconds field. warn=False suppresses the warning
    # that we are losing the nanoseconds; however, this is intended.
    return pd.Timestamp(ts.to_pydatetime(warn=False), tz='UTC')


def ensure_utc(time, tz='UTC'):
    """
    Normalize a time. If the time is tz-naive, assume it is UTC.
    """
    if not time.tzinfo:
        time = time.replace(tzinfo=pytz.timezone(tz))
    return time.replace(tzinfo=pytz.utc)


def _out_of_range_error(a, b=None, var='offset'):
    start = 0
    if b is None:
        end = a - 1
    else:
        start = a
        end = b - 1
    return ValueError(
        '{var} must be in between {start} and {end} inclusive'.format(
            var=var,
            start=start,
            end=end,
        )
    )


def _td_check(td):
    seconds = td.total_seconds()

    # 43200 seconds = 12 hours
    if 60 <= seconds <= 43200:
        return td
    else:
        raise ValueError('offset must be in between 1 minute and 12 hours, '
                         'inclusive.')


def _build_offset(offset, kwargs, default):
    """
    Builds the offset argument for event rules.
    """
    # Filter down to just kwargs that were actually passed.
    kwargs = {k: v for k, v in six.iteritems(kwargs) if v is not None}
    if offset is None:
        if not kwargs:
            return default  # use the default.
        else:
            return _td_check(datetime.timedelta(**kwargs))
    elif kwargs:
        raise ValueError('Cannot pass kwargs and an offset')
    elif isinstance(offset, datetime.timedelta):
        return _td_check(offset)
    else:
        raise TypeError("Must pass 'hours' and/or 'minutes' as keywords")


def _build_date(date, kwargs):
    """
    Builds the date argument for event rules.
    """
    if date is None:
        if not kwargs:
            raise ValueError('Must pass a date or kwargs')
        else:
            return datetime.date(**kwargs)

    elif kwargs:
        raise ValueError('Cannot pass kwargs and a date')
    else:
        return date


def _build_time(time, kwargs):
    """
    Builds the time argument for event rules.
    """
    tz = kwargs.pop('tz', 'UTC')
    if time:
        if kwargs:
            raise ValueError('Cannot pass kwargs and a time')
        else:
            return ensure_utc(time, tz)
    elif not kwargs:
        raise ValueError('Must pass a time or kwargs')
    else:
        return datetime.time(**kwargs)


def _time_to_micros(time):
    """Convert a time into microseconds since midnight.
    Parameters
    ----------
    time : datetime.time
        The time to convert.
    Returns
    -------
    us : int
        The number of microseconds since midnight.
    Notes
    -----
    This does not account for leap seconds or daylight savings.
    """
    seconds = time.hour * 60 * 60 + time.minute * 60 + time.second
    return 1000000 * seconds + time.microsecond


def timedelta_to_integral_seconds(delta):
    """
    Convert a pd.Timedelta to a number of seconds as an int.
    """
    return int(delta.total_seconds())


def timedelta_to_integral_minutes(delta):
    """
    Convert a pd.Timedelta to a number of minutes as an int.
    """
    return timedelta_to_integral_seconds(delta) // 60


def normalize_quarters(years, quarters):
    return years * 4 + quarters - 1


def split_normalized_quarters(normalized_quarters):
    years = normalized_quarters // 4
    quarters = normalized_quarters % 4
    return years, quarters + 1


def aggregate_returns(returns, convert_to):
    """
    Aggregates returns by week, month, or year.

    Parameters
    ----------
    returns : pd.Series
       Daily returns of the strategy, noncumulative.
        - See full explanation in :func:`~empyrical.stats.cum_returns`.
    convert_to : str
        Can be 'weekly', 'monthly', or 'yearly'.

    Returns
    -------
    aggregated_returns : pd.Series
    """

    def cumulate_returns(x):
        # return cum_returns(x).iloc[-1]
        raise NotImplementedError()

    if convert_to == 'weekly':
        grouping = [lambda x: x.year, lambda x: x.isocalendar()[1]]
    elif convert_to == 'monthly':
        grouping = [lambda x: x.year, lambda x: x.month]
    elif convert_to == 'quarterly':
        grouping = [lambda x: x.year, lambda x: int(math.ceil(x.month/3.))]
    elif convert_to == 'yearly':
        grouping = [lambda x: x.year]
    else:
        raise ValueError(
            'convert_to must be {}, {} or {}'.format('weekly', 'monthly', 'yearly')
        )

    return returns.groupby(grouping).apply(cumulate_returns)