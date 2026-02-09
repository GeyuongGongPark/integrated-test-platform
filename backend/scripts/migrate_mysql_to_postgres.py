import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData, Table, text


def get_mysql_url():
    password = quote_plus(os.environ.get("MYSQL_PASSWORD", "1q2w#E$R"))
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    user = os.environ.get("MYSQL_USER", "root")
    dbname = os.environ.get("MYSQL_DB", "test_management")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"


def get_postgres_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def quote_table(name):
    return f"\"{name}\""


def truncate_tables(pg_conn, table_names):
    quoted = ", ".join(quote_table(name) for name in table_names)
    pg_conn.execute(text(f"TRUNCATE {quoted} CASCADE"))


def reset_sequence(pg_conn, table_name, pk_column):
    table_quoted = quote_table(table_name)
    col_quoted = quote_table(pk_column)
    sql = (
        "SELECT setval("
        f"pg_get_serial_sequence('{table_quoted}', '{pk_column}'), "
        f"COALESCE((SELECT MAX({col_quoted}) FROM {table_quoted}), 1), "
        "true)"
    )
    try:
        pg_conn.execute(text(sql))
    except Exception:
        # 시퀀스가 없는 테이블은 무시
        pass


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root, "..", ".env"))

    mysql_url = get_mysql_url()
    pg_url = get_postgres_url()

    mysql_engine = create_engine(mysql_url)
    pg_engine = create_engine(pg_url)

    mysql_inspector = inspect(mysql_engine)
    pg_inspector = inspect(pg_engine)

    mysql_tables = mysql_inspector.get_table_names()
    pg_tables = pg_inspector.get_table_names()

    mysql_lookup = {name.lower(): name for name in mysql_tables}
    tables_to_copy = [t for t in pg_tables if t.lower() in mysql_lookup]

    if not tables_to_copy:
        raise RuntimeError("No matching tables found between MySQL and Postgres")

    mysql_metadata = MetaData()
    pg_metadata = MetaData()
    mysql_tables_map = {}
    pg_tables_map = {}

    deps = {t: set() for t in tables_to_copy}
    for table_name in tables_to_copy:
        for fk in pg_inspector.get_foreign_keys(table_name):
            ref_table = fk.get("referred_table")
            if ref_table and ref_table in deps and ref_table != table_name:
                deps[table_name].add(ref_table)

    ordered_tables = []
    ready = [t for t, d in deps.items() if not d]
    while ready:
        current = ready.pop()
        ordered_tables.append(current)
        for table_name, required in deps.items():
            if current in required:
                required.remove(current)
                if not required and table_name not in ordered_tables and table_name not in ready:
                    ready.append(table_name)

    if len(ordered_tables) != len(tables_to_copy):
        remaining = [t for t in tables_to_copy if t not in ordered_tables]
        ordered_tables.extend(remaining)

    for table_name in ordered_tables:
        mysql_name = mysql_lookup[table_name.lower()]
        mysql_tables_map[table_name] = Table(
            mysql_name, mysql_metadata, autoload_with=mysql_engine
        )
        pg_tables_map[table_name] = Table(
            table_name, pg_metadata, autoload_with=pg_engine
        )

    with pg_engine.begin() as pg_conn:
        pg_conn.execute(
            text('ALTER TABLE "TestResults" DROP CONSTRAINT IF EXISTS "check_test_reference"')
        )
        truncate_tables(pg_conn, ordered_tables)

    for table_name in ordered_tables:
        mysql_table = mysql_tables_map[table_name]
        pg_table = pg_tables_map[table_name]
        boolean_columns = []
        for col in pg_table.columns:
            try:
                if col.type.python_type is bool:
                    boolean_columns.append(col.name)
            except Exception:
                if str(col.type).lower() == "boolean":
                    boolean_columns.append(col.name)

        print(f"[COPY] {table_name}")
        with mysql_engine.connect() as mysql_conn, pg_engine.begin() as pg_conn:
            result = mysql_conn.execute(mysql_table.select()).mappings()
            rows = result.fetchmany(1000)
            while rows:
                payload = []
                for row in rows:
                    data = dict(row)
                    for col_name in boolean_columns:
                        if col_name not in data:
                            continue
                        value = data[col_name]
                        if value is None:
                            continue
                        if isinstance(value, bool):
                            continue
                        if isinstance(value, (int, float)):
                            data[col_name] = bool(int(value))
                        elif isinstance(value, str):
                            data[col_name] = value.lower() in ("1", "true", "t", "yes", "y")
                    payload.append(data)
                if payload:
                    pg_conn.execute(pg_table.insert(), payload)
                rows = result.fetchmany(1000)

            pk_cols = [col.name for col in pg_table.primary_key.columns]
            if len(pk_cols) == 1 and pk_cols[0] == "id":
                reset_sequence(pg_conn, table_name, "id")

    print("✅ Migration complete")


if __name__ == "__main__":
    main()
