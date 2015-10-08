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
        name text
);

CREATE TABLE matches (
        id serial PRIMARY KEY,
        winner int REFERENCES players(id),
        loser int REFERENCES players(id)
);


CREATE VIEW v_wins AS
        SELECT players.id,
            COUNT(matches.winner) AS wins
                FROM players LEFT JOIN matches
                    ON players.id = matches.winner
                GROUP BY players.id
                ORDER BY wins;

CREATE VIEW v_match_counts AS
        SELECT players.id,
            COUNT (matches.winner) AS num_matches
                FROM players LEFT JOIN matches
                    ON players.id = matches.winner
                    OR players.id = matches.loser
                GROUP BY players.id
                ORDER BY num_matches desc;
/*
CREATE VIEW v_results AS
        SELECT v_wins.id, wins, num_matches
                FROM v_wins, v_match_counts
                    WHERE v_wins.id=v_match_counts.id
                ORDER BY wins desc;
*/
-- Try view a different way
CREATE VIEW v_standings AS
        SELECT players.id, players.name, SUM(v_wins.wins) AS wins, SUM(v_match_counts.num_matches) AS matches
                FROM players JOIN v_wins ON players.id = v_wins.id
                             JOIN v_match_counts ON players.id = v_match_counts.id
                GROUP BY players.id;
