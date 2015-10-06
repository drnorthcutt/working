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

CREATE VIEW v_wins AS
        SELECT players.id, players.name,
            COUNT(matches.winner) AS wins
            from players LEFT JOIN matches
                ON players.id = matches.winner
            GROUP BY players.id, name, winner
            ORDER BY winner;


CREATE VIEW v_matches AS
        SELECT players.id, name,
            COUNT(*) AS num_matches
            FROM players, matches
                WHERE players.id = matches.winner
                OR players.id = matches.loser
            GROUP BY players.id
            ORDER BY wins desc;

CREATE VIEW results AS
        select v_wins.id, v_wins.name, wins, num_matches
            from v_wins, v_matches
            where v_wins.id=v_matches.id
            order by wins desc;




