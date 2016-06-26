# pgpart

[![Build Status](https://travis-ci.org/achiku/pgpart.svg?branch=master)](https://travis-ci.org/achiku/pgpart)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/achiku/pgpart/master/LICENSE)
[![Requirements Status](https://requires.io/github/achiku/pgpart/requirements.svg?branch=master)](https://requires.io/github/achiku/pgpart/requirements/?branch=master)

## Description

Creating PostgreSQL partition table DDL should be easier.


## Why created

Unlike MySQL and Oracle, PostgreSQL uses table inheritance and triggers (or rules) to realize horizontal table partitioning. Manually writing child tables with check constraints, and triggers with bunch of if-else statements is boring, time cunsuming, and error-prone at the same time. Given parent table name, partition key name, and time range, this tool generates child tables/trigger DDL so that developers don't have to spend too much time on writing/checking partitioning DDLs.


## Installation

```
pip install pgpart
```

## Usage

### Monthly Range Partition

```
pgpart rangep generate -n sale -k sold_at -s 201501 -e 201602
```
