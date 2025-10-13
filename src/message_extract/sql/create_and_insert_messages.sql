CREATE TABLE IF NOT EXISTS metadb.messages AS
FROM
    message_table
LIMIT
    0;
INSERT INTO
    metadb.messages
SELECT
    *
FROM
    message_table;
