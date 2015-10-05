-- Table definitions for the tournament project.
--
/*
Drop the database if it exists.
Create the database and establish the schema.
*/

DROP DATABASE tournament;
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (
        id serial PRIMARY KEY,
        name text,
        wins int,
        matches int
);

CREATE TABLE matches (
        id serial PRIMARY KEY,
        winner int REFERENCES players(id),
        loser int REFERENCES players(id)
);

CREATE VIEW results as
        select players.id, players.name, count(matches.winner)
            from players left join matches
                on players.id = matches.winner
        group by players.id,name,winner
        order by winner;

