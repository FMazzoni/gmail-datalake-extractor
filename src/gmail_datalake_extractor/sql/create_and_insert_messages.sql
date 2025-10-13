CREATE TABLE IF NOT EXISTS metadb.messages (
    id VARCHAR,
    threadId VARCHAR,
    labelIds VARCHAR [],
    snippet VARCHAR,
    historyId VARCHAR,
    internalDate VARCHAR,
    payload VARCHAR,
    sizeEstimate INTEGER,
    raw VARCHAR
);
INSERT INTO
    metadb.messages
SELECT
    *
FROM
    message_table;
