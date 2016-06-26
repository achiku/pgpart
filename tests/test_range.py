# -*- coding: utf-8 -*-
from datetime import datetime

import pytest


@pytest.mark.parametrize('start, end, expected', [
    (datetime(2016, 11, 1), datetime(2016, 11, 1), []),
    (
        datetime(2016, 10, 1), datetime(2016, 12, 1),
        [
            {'start': datetime(2016, 10, 1), 'end': datetime(2016, 11, 1)},
            {'start': datetime(2016, 11, 1), 'end': datetime(2016, 12, 1)},
        ]
    ),
    (
        datetime(2016, 11, 1), datetime(2017, 2, 1),
        [
            {'start': datetime(2016, 11, 1), 'end': datetime(2016, 12, 1)},
            {'start': datetime(2016, 12, 1), 'end': datetime(2017, 1, 1)},
            {'start': datetime(2017, 1, 1), 'end': datetime(2017, 2, 1)},
        ]
    ),
])
def test_month_timerange(start, end, expected):
    from pgpart.rangep import month_timerange
    l = month_timerange(start, end)
    assert l == expected


def test_generate_partitioned_table_ddl():
    from pgpart.rangep import generate_partitioned_table_ddl
    parent_name = 'sale'
    partition_key = 'sold_at'
    month_range = [
        {'start': datetime(2016, 11, 1), 'end': datetime(2016, 12, 1)},
    ]
    ddls = generate_partitioned_table_ddl(parent_name, partition_key, month_range)
    s = """
    CREATE TABLE sale_201611 (
        CHECK (sold_at >= '2016-11-01' AND sold_at < '2016-12-01')
    ) INHERITS (sale);"""

    assert len(ddls) == 1
    assert ddls[0] == s


def test_generate_trigger_condition():
    from pgpart.rangep import generate_trigger_conditions
    parent_name = 'sale'
    partition_key = 'sold_at'
    month_range = [
        {'start': datetime(2016, 11, 1), 'end': datetime(2016, 12, 1)},
        {'start': datetime(2016, 12, 1), 'end': datetime(2017, 1, 1)},
    ]
    conditions = generate_trigger_conditions(parent_name, partition_key, month_range)
    s = """
    IF (NEW.sold_at >= '2016-11-01' AND NEW.sold_at < '2016-12-01') THEN
        INSERT INTO sale_201611 VALUES (NEW.*);

    ELSIF (NEW.sold_at >= '2016-12-01' AND NEW.sold_at < '2017-01-01') THEN
        INSERT INTO sale_201612 VALUES (NEW.*);"""

    assert len(conditions) == 2
    assert '\n'.join(conditions) == s


def test_generate_trigger():
    from pgpart.rangep import generate_trigger
    parent_name = 'sale'
    partition_key = 'sold_at'
    month_range = [
        {'start': datetime(2016, 11, 1), 'end': datetime(2016, 12, 1)},
        {'start': datetime(2016, 12, 1), 'end': datetime(2017, 1, 1)},
    ]
    ddl = generate_trigger(parent_name, partition_key, month_range)
    s = """
    CREATE OR REPLACE FUNCTION sale_insert_trigger()
    RETURNS TRIGGER AS $$

    BEGIN
    IF (NEW.sold_at >= '2016-11-01' AND NEW.sold_at < '2016-12-01') THEN
        INSERT INTO sale_201611 VALUES (NEW.*);
    ELSIF (NEW.sold_at >= '2016-12-01' AND NEW.sold_at < '2017-01-01') THEN
        INSERT INTO sale_201612 VALUES (NEW.*);
    ELSE
        RAISE EXCEPTION 'Date out of range. Fix the sale_insert_trigger() function.';
    END IF;

    RETURN NULL;
    END;
    $$
    LANGUAGE plpgsql;"""

    assert ddl == s
