-- Table definitions for the tournament project.
--
/*
Drop the database if it exists.
Create the database and establish the schema.
Create views.
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


-- Display number of wins
CREATE VIEW v_wins AS
        SELECT players.id,
            COUNT(matches.winner) AS wins
                FROM players
                    LEFT JOIN matches
                        ON players.id = matches.winner
                GROUP BY players.id
                ORDER BY wins;

-- Display number of matches per each player
CREATE VIEW v_match_counts AS
        SELECT players.id,
            COUNT (matches.winner) AS num_matches
                FROM players
                    LEFT JOIN matches
                        ON players.id = matches.winner
                        OR players.id = matches.loser
                GROUP BY players.id
                ORDER BY num_matches desc;

-- Display standings
CREATE VIEW v_standings AS
        SELECT players.id, players.name,
            SUM(v_wins.wins) AS wins,
            SUM(v_match_counts.num_matches) AS matches
                FROM players
                    JOIN v_wins
                        ON players.id = v_wins.id
                    JOIN v_match_counts
                        ON players.id = v_match_counts.id
                GROUP BY players.id;

-- Display score
CREATE VIEW v_score AS
        SELECT players.id,
            COUNT(matches.winner)*3 AS score
                FROM players
                    LEFT JOIN matches
                        ON players.id = matches.winner
                GROUP BY players.id
                ORDER BY score;

-- Display match-wins
CREATE VIEW v_matchwins AS
        SELECT v_wins.id,
               players.name,
              (v_wins.wins * 3) / (v_match_counts.num_matches * 3)::float AS match_wins
                FROM v_wins
                    JOIN v_match_counts
                        ON v_match_counts.id = v_wins.id
                    JOIN players
                        ON players.id = v_match_counts.id;

-- Display opponent match wins
CREATE VIEW v_omw AS
        SELECT opponent.id,
                SUM(opponent.wins)/v_match_counts.num_matches AS omw
                FROM (
                        SELECT matches.winner AS id,
                               GREATEST (0.33, (v_matchwins.match_wins)) AS wins
                                FROM matches
                                    JOIN v_matchwins
                                        ON matches.loser= v_matchwins.id
                                GROUP BY matches.winner,
                                         v_matchwins.name,
                                         v_matchwins.match_wins
                    UNION ALL
                        SELECT matches.loser AS id,
                                GREATEST (0.33, (v_matchwins.match_wins)) AS wins
                                FROM matches
                                    JOIN v_matchwins
                                        ON matches.winner = v_matchwins.id
                                GROUP BY matches.loser,
                                        v_matchwins.name,
                                        v_matchwins.match_wins) AS opponent,
                       v_match_counts
                        WHERE opponent.id = v_match_counts.id
                GROUP BY opponent.id, v_match_counts.num_matches;

-- Display final results
CREATE VIEW v_results AS
        SELECT v_standings.id,
                v_standings.name,
                v_standings.wins,
                v_standings.matches,
                v_score.score,
                v_matchwins.match_wins AS matchwins,
                v_omw.omw
                FROM v_standings
                    LEFT JOIN v_score
                        ON v_standings.id = v_score.id
                    LEFT JOIN v_matchwins
                        ON v_standings.id = v_matchwins.id
                    LEFT JOIN v_omw
                        ON v_standings.id = v_omw.id
                ORDER by wins desc, score, matchwins desc, omw desc;
