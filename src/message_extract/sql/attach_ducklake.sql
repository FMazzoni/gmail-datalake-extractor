{% if db_mode == "duckdb" %}
    attach 'ducklake:{{ DB_DUCKDB_FILE }}' AS metadb (
        data_path 'data/',
        metadata_schema 'messages'
    );
{% else %}
    attach 'ducklake:postgres://{{ POSTGRES_USER }}:{{ POSTGRES_PASSWORD }}@{{ POSTGRES_HOST }}:{{ POSTGRES_PORT }}/{{ POSTGRES_DB }}' AS metadb (
        data_path 'data/',
        metadata_schema 'messages',
        encrypted
    );
{% endif %}
