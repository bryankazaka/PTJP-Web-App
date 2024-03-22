CREATE DATABASE IF NOT EXISTS PTJPApp;
USE PTJPApp;

CREATE TABLE IF NOT EXISTS searches (
	id              int(11) AUTO_INCREMENT,
    username        varchar(50) NOT NULL,
    search_from     varchar(100) NOT NULL,
    search_to       varchar(100) NOT NULL,
    search_schedule varchar(100) NOT NULL,
    search_filter   varchar(100) NOT NULL,
    search_time     varchar(100) NOT NULL,
    image           varchar(1000) NOT NULL,
    route           varchar(10000) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
	username  varchar(100) NOT NULL,
    pwd       varchar(100) NOT NULL,
    logged_in varchar(100) NOT NULL,
    PRIMARY KEY (username)
);