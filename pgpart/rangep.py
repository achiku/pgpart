# -*- coding: utf-8 -*-
from datetime import datetime

import click
from dateutil import relativedelta


@click.group()
def cli():
    """Range partitioning CLI group"""
    pass


def validate_month(ctx, param, value):
    try:
        dt = datetime.strptime(value+"01", "%Y%m%d")
        return dt
    except ValueError:
        raise click.BadParameter('month need to be in format YYYYMM')


@cli.command(help='Generate monthly range partition DDL')
@click.option('--parent-name', '-n', required=True, help='parent table name')
@click.option('--partition-key', '-k', required=True, help='partition key column name')
@click.option('--start-month', '-s',
              required=True, callback=validate_month, help='monthly range partition start date (YYYYMM)')
@click.option('--end-month', '-e',
              required=True, callback=validate_month, help='monthly range partition end date (YYYYMM)')
def generate(parent_name, partition_key, start_month, end_month):
    """Generate monthly range partition DDL"""
    duration = month_timerange(start_month, end_month)
    table_ddls = generate_partitioned_table_ddl(parent_name, partition_key, duration)
    trigger_ddl = generate_trigger(parent_name, partition_key, duration)

    click.echo('\n'.join(table_ddls))
    click.echo(trigger_ddl)


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


def month_timerange(start_date, end_date):
    intervals = []
    dt = start_date
    while dt != end_date:
        nextdt = dt + relativedelta.relativedelta(months=1)
        intervals.append({'start': dt, 'end': nextdt})
        dt = nextdt
    return intervals


def generate_partitioned_table_ddl(parent_name, partition_key, month_range):
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


def generate_trigger_conditions(parent_name, partition_key, month_range):
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


def generate_trigger(parent_name, partition_key, month_range):
    cond = ''
    for c in generate_trigger_conditions(parent_name, partition_key, month_range):
        cond = cond + c
    return create_trigger_for_partitioned_table_tmpl.format(
        parent_name=parent_name,
        conditions=cond,
    )
