# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from dateutil import relativedelta

partitioned_table_tmpl = """
    CREATE TABLE {parent_name}_{year_month} (
        CHECK ({partition_key} >= '{start_date}' and {partition_key} < '{end_date}')
    ) INHERITS ({parent_name});"""

trigger_conditions_tmpl = """
    {ifelse} (NEW.{partition_key} >= '{start_date}' NEW.{partition_key} < '{end_date}') THEN
        INSERT INTO {parent_name}_{year_month} VALUES (NEW.*);"""

create_trigger_for_partitioned_table_tmpl = """
    CREATE OR REPLACE FUNCTION {parent_name}_insert_trigger()
    RETURNS TRIGGER AS $$

    BEGIN{conditions}
    END IF;

    RETURN NULL;
    END;
    $$
    LANGUAGE plpgsql;"""


def month_timerange(start_date: datetime, end_date: datetime) -> List:
    intervals = []
    dt = start_date
    while dt != end_date:
        nextdt = dt + relativedelta.relativedelta(months=1)
        intervals.append({'start': dt, 'end': nextdt})
        dt = nextdt
    return intervals


def generate_partitioned_table_ddl(parent_name: str, partition_key: str, month_range: List) -> List[str]:
    ddls = []
    for d in month_range:
        ddl = partitioned_table_tmpl.format(
            parent_name=parent_name,
            partition_key=partition_key,
            year_month='{:%Y%m}'.format(d['start']),
            start_date='{:%Y-%m-%d}'.format(d['start']),
            end_date='{:%Y-%m-%d}'.format(d['end']),
        )
        ddls.append(ddl)
    return ddls


def generate_trigger_conditions(parent_name: str, partition_key: str, month_range: List) -> List[str]:
    conditions = []
    for i, d in enumerate(month_range):
        ifelse = 'IF' if i == 0 else 'ELSE'
        condition = trigger_conditions_tmpl.format(
            ifelse=ifelse,
            parent_name=parent_name,
            partition_key=partition_key,
            year_month='{:%Y%m}'.format(d['start']),
            start_date='{:%Y-%m-%d}'.format(d['start']),
            end_date='{:%Y-%m-%d}'.format(d['end']),
        )
        conditions.append(condition)
    return conditions


def generate_trigger(parent_name: str, partition_key: str, month_range: List) -> str:
    cond = ''
    for c in generate_trigger_conditions(parent_name, partition_key, month_range):
        cond = cond + c
    return create_trigger_for_partitioned_table_tmpl.format(
        parent_name=parent_name,
        conditions=cond,
    )
