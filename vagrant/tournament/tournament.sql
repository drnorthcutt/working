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
        loser int REFERENCES players(id),
        draw bool DEFAULT False
);

-- Display number of wins
CREATE VIEW v_wins AS
        SELECT players.id,
            COUNT(matches.winner) AS wins
                FROM players
                    LEFT JOIN matches
                        ON players.id = matches.winner
                        AND matches.draw != 'True'
                GROUP BY players.id
                ORDER BY wins DESC;

-- Display number of draws
CREATE VIEW v_ties AS
        SELECT ties.id,
            SUM (ties.num) as draws
                FROM (
                        SELECT players.id,
                            COUNT (matches.winner) AS num
                                FROM players
                                    LEFT JOIN matches
                                        ON matches.draw = 'True'
                                        AND players.id = matches.winner
                                GROUP BY players.id
                    UNION ALL
                        SELECT players.id,
                            COUNT (matches.loser) AS num
                                FROM players
                                    LEFT JOIN matches
                                        ON matches.draw = 'True'
                                        AND players.id = matches.loser
                                GROUP BY players.id
                     ) AS ties
                GROUP BY id;

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
            SUM(v_match_counts.num_matches) AS matches,
            SUM(v_ties.draws) as ties
                FROM players
                    JOIN v_wins
                        ON players.id = v_wins.id
                    JOIN v_match_counts
                        ON players.id = v_match_counts.id
                    JOIN v_ties
                        ON players.id = v_ties.id
                GROUP BY players.id
                ORDER BY wins DESC;

-- Display score (wins = 3, losses =0, draws = 1)
CREATE VIEW v_score AS
        SELECT scores.id,
            SUM (scores.points) AS score
            FROM (
                    SELECT players.id,
                        COUNT(matches.winner)*3 AS points
                            FROM players
                                LEFT JOIN matches
                                    ON players.id = matches.winner
                                    AND matches.draw != 'True'
                            GROUP BY players.id
                UNION ALL
                    SELECT players.id,
                        COUNT(matches.winner) AS points
                            FROM players
                                JOIN matches
                                    ON matches.draw
                                    AND players.id = matches.winner
                            GROUP BY players.id
                UNION ALL
                    SELECT players.id,
                        COUNT(matches.loser) AS points
                            FROM players
                                JOIN matches
                                    ON matches.draw
                                    AND players.id = matches.loser
                            GROUP BY players.id
                 ) AS scores
            GROUP BY id
            Order by score;

-- Display scores from BYES as a negative number, to remove from match points
CREATE VIEW v_byeScore AS
        SELECT scores.id,
                SUM(-scores.points) AS score
                    FROM (
                            SELECT players.id,
                                COUNT (matches.winner)*3 AS points
                                    FROM players
                                        LEFT JOIN matches
                                            ON players.id = matches.winner
                                            AND matches.loser = 9999
                                    GROUP BY players.id
                         ) AS scores
                    GROUP BY scores.id;

-- Remove BYE wins from score. (Used for matchwins and omw.)
CREATE VIEW byeGone AS
        SELECT byebye.id,
            SUM (byebye.corrected) AS score
                FROM (
                        SELECT v_score.id,
                                v_score.score AS corrected
                                FROM v_score
                    UNION
                        SELECT v_byeScore.id,
                                v_byeScore.score AS corrected
                                FROM v_byescore
                     ) AS byebye
                GROUP BY byebye.id;

-- BYE match total
CREATE VIEW v_matchBye AS
        SELECT players.id,
            COUNT (matches.winner) AS num_matches
                FROM players
                    LEFT JOIN matches
                        ON players.id = matches.winner
                        AND matches.loser = 9999
                GROUP BY players.id;


-- Remove BYE matches from player match totals. (Used for match wins and omw.)
CREATE VIEW matchByeGone AS
        SELECT matchbye.id,
            SUM (matchbye.corrected) as num_matches
                FROM (
                        SELECT id,
                                num_matches AS corrected
                                FROM v_match_counts
                    UNION
                        SELECT id,
                                (- num_matches) AS corrected
                                FROM v_matchBye
                     ) AS matchbye
                GROUP BY matchbye.id;

-- Match-wins Corrected for BYES
CREATE VIEW v_matchwins AS
        SELECT byeGone.id,
               players.name,
               (
                  (byeGone.score) / ((matchByeGone.num_matches) * 3)

               )::float AS match_wins
                FROM byeGone
                    JOIN matchByeGone
                        ON matchByeGone.id = byeGone.id
                    JOIN players
                        ON players.id = byeGone.id;

-- Opponent match wins
CREATE VIEW v_omw AS
        SELECT opponent.id,
               (
                    (SUM(opponent.wins)) / matchByeGone.num_matches
               )::float AS omw
                FROM (
                        SELECT matches.winner AS id,
                               matches.draw,
                               GREATEST (0.33, (v_matchwins.match_wins)) AS wins
                                FROM matches
                                    JOIN v_matchwins
                                        ON matches.loser= v_matchwins.id
                                GROUP BY matches.winner,
                                         v_matchwins.name,
                                         v_matchwins.match_wins,
                                         matches.draw
                    UNION ALL
                        SELECT matches.loser AS id,
                                matches.draw,
                                GREATEST (0.33, (v_matchwins.match_wins)) AS wins
                                FROM matches
                                    JOIN v_matchwins
                                        ON matches.winner = v_matchwins.id
                                GROUP BY matches.loser,
                                        v_matchwins.name,
                                        v_matchwins.match_wins,
                                        matches.draw
                     ) AS opponent,
                        matchByeGone
                        WHERE opponent.id = matchByeGone.id
                GROUP BY opponent.id, matchByeGone.num_matches;

-- Final player results with tie breakers
CREATE VIEW v_results AS
        SELECT v_standings.id,
                v_standings.name,
                v_standings.wins,
                v_ties.draws,
                v_standings.matches,
                v_score.score,
                GREATEST (0.33, v_matchwins.match_wins) AS matchwins,
                v_omw.omw
                FROM v_standings
                    LEFT JOIN v_score
                        ON v_standings.id = v_score.id
                    LEFT JOIN v_ties
                        ON v_standings.id = v_ties.id
                    LEFT JOIN v_matchwins
                        ON v_standings.id = v_matchwins.id
                    LEFT JOIN v_omw
                        ON v_standings.id = v_omw.id
                ORDER BY score DESC, matchwins DESC, omw DESC;
