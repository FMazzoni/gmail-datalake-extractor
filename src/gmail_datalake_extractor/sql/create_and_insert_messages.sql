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
MERGE INTO metadb.messages AS target USING message_table AS source
ON (
    target.id = source.id
)
WHEN matched THEN
UPDATE
    WHEN NOT matched THEN
INSERT;
