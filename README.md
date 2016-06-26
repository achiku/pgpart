# pgpart

[![Build Status](https://travis-ci.org/achiku/pgpart.svg?branch=master)](https://travis-ci.org/achiku/pgpart)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/achiku/pgpart/master/LICENSE)

## Description

Creating PostgreSQL partition table DDL should be easier.


## Why created

Unlike MySQL and Oracle, PostgreSQL uses table inheritance and trigger (or rule) to realize horizontal table partitioning. Writing child tables with check constraints and triggers by hands is boring, and dangerous at the same time. This cli tool generates child tables/trigger DDL so that developers don't have to spend time to write/check DDLs for partitioning.


## Limitation

This tool is created just for generating table partitioning DDLs, and does not provide functionality to version control DDLs. Developers should consider using different tools, like alembic + SQLAlchemy, to manage DDLs in your VCS.


## Installation

```
pip install pgpart
```

## Usage

### Monthly Range Partition

```
pgpart rangep generate -n sale -k sold_at -s 201501 -e 201602
```
