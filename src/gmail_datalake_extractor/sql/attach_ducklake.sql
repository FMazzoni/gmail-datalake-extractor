{% if db_mode == "duckdb" %}
    attach 'ducklake:{{ DB_DUCKDB_FILE }}' AS metadb (
        data_path '{{ DUCKLAKE_DATA_PATH }}',
        metadata_schema '{{ DUCKLAKE_METADATA_SCHEMA }}'
    );
{% else %}
    attach 'ducklake:postgres: user={{ POSTGRES_USER }} password={{ POSTGRES_PASSWORD }} host={{ POSTGRES_HOST }} port={{ POSTGRES_PORT }} dbname={{ POSTGRES_DB }}' AS metadb (
        data_path '{{ DUCKLAKE_DATA_PATH }}',
        metadata_schema '{{ DUCKLAKE_METADATA_SCHEMA }}',
        encrypted
    );
{% endif %}
