# pgpart

[![Build Status](https://travis-ci.org/achiku/pgpart.svg?branch=master)](https://travis-ci.org/achiku/pgpart)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/achiku/pgpart/master/LICENSE)
[![Requirements Status](https://requires.io/github/achiku/pgpart/requirements.svg?branch=master)](https://requires.io/github/achiku/pgpart/requirements/?branch=master)

## Description

Creating PostgreSQL partitioned table DDLs should be easier.


## Why created

Unlike MySQL and Oracle, PostgreSQL uses table inheritance and triggers (or rules) to realize horizontal table partitioning. Manually writing child tables with check constraints, and triggers with bunch of if-else statements is boring, time cunsuming, and error-prone. This tool generates child tables/trigger DDLs with given parent table name, partition key name, and time range, so that developers don't have to spend too much time on writing/checking partitioning DDLs.


## Installation

```
pip install pgpart
```

## Usage

##### Create/Drop Monthly Range Partition

```
$ pgpart rangep create --parent-name sale --partition-key sold_at --start-month 201608 --end-month 201611
```

```sql
    CREATE TABLE sale_201608 (
        CHECK (sold_at >= '2016-08-01' AND sold_at < '2016-09-01')
    ) INHERITS (sale);

    CREATE TABLE sale_201609 (
        CHECK (sold_at >= '2016-09-01' AND sold_at < '2016-10-01')
    ) INHERITS (sale);

    CREATE TABLE sale_201610 (
        CHECK (sold_at >= '2016-10-01' AND sold_at < '2016-11-01')
    ) INHERITS (sale);

    CREATE OR REPLACE FUNCTION sale_insert_trigger()
    RETURNS TRIGGER AS $$

    BEGIN
    IF (NEW.sold_at >= '2016-08-01' AND NEW.sold_at < '2016-09-01') THEN
        INSERT INTO sale_201608 VALUES (NEW.*);
    ELSIF (NEW.sold_at >= '2016-09-01' AND NEW.sold_at < '2016-10-01') THEN
        INSERT INTO sale_201609 VALUES (NEW.*);
    ELSIF (NEW.sold_at >= '2016-10-01' AND NEW.sold_at < '2016-11-01') THEN
        INSERT INTO sale_201610 VALUES (NEW.*);
    ELSE
        RAISE EXCEPTION 'Date out of range. Fix the sale_insert_trigger() function.';
    END IF;

    RETURN NULL;
    END;
    $$
    LANGUAGE plpgsql;

    CREATE TRIGGER insert_sale_trigger
        BEFORE INSERT ON sale
        FOR EACH ROW EXECUTE PROCEDURE sale_insert_trigger();
```

```
$ pgpart rangep drop --parent-name sale --partition-key sold_at --start-month 201608 --end-month 201611
```

```sql
    DROP TABLE sale_201608 ;

    DROP TABLE sale_201609 ;

    DROP TABLE sale_201610 ;

    DROP TRIGGER insert_sale_trigger ON sale ;

    DROP FUNCTION sale_insert_trigger() ;
```


##### Create/Drop Yearly Range Partition

- not implemented yet


##### Create/Drop Daily Range Partition

- not implemented yet


##### Create/Drop List Partition

- not implemented yet
