{% if db_mode == "duckdb" %}
    attach 'ducklake:{{ DB_DUCKDB_FILE }}' AS metadb (
        data_path '{{ DUCKLAKE_DATA_PATH }}',
        metadata_schema '{{ DUCKLAKE_METADATA_SCHEMA }}'
    );
{% else %}
    attach 'ducklake:postgres://{{ POSTGRES_USER }}:{{ POSTGRES_PASSWORD }}@{{ POSTGRES_HOST }}:{{ POSTGRES_PORT }}/{{ POSTGRES_DB }}' AS metadb (
        data_path '{{ DUCKLAKE_DATA_PATH }}',
        metadata_schema '{{ DUCKLAKE_METADATA_SCHEMA }}',
        encrypted
    );
{% endif %}
