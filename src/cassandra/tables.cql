create keyspace if not exists project with replication = {'class' : 'SimpleStrategy', 'replication_factor':1};

use project;

drop table if exists project.users;
drop table if exists project.pages;

create table if not exists project.users
(
    id        bigint,
    name      text,
    page_id   bigint,
    timestamp timestamp,

    primary key ((id), timestamp)
)
            with clustering order by (timestamp desc);


create table if not exists project.pages
(
    id        bigint,
    url       text,
    title     text,
    domain    text,
    namespace int,

    primary key ((id), domain)
)
            with clustering order by (domain desc);

create table if not exists project.stats_created_pages
(
    time_start text,
    time_end   text,
    statistics map<text,bigint>,
    primary key (time_start)
);


create type custom_stats_bots (domain text, created_by_bots bigint);

create table if not exists project.stats_domains
(
    time_start text,
    time_end   text,
    statistics frozen<list<custom_stats_bots>>,
    primary key (time_start)
);


create type custom_stats_users (
    user_id bigint, user_name text, number_of_pages bigint, page_titles list<text>
    );

create table if not exists project.stats_users
(
    time_start text,
    time_end   text,
    users      frozen<list<custom_stats_users>>,
    primary key (time_start)
);
