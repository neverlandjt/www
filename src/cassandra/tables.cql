create keyspace if not exists project with replication = {'class' : 'SimpleStrategy', 'replication_factor':1};

use project;

CREATE TABLE project.users
(
    id          bigint,
    name        text,
    page_id     bigint,
    timestamp   timestamp,

    PRIMARY KEY ((id), timestamp)
);

CREATE TABLE project.pages
(
    id          bigint,
    url         text,
    title       text,
    domain      text,
    namespace   int,

    PRIMARY KEY ((id), domain)
);
