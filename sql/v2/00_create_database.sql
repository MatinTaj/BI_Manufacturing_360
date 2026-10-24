-- Run separately against postgres, outside a transaction. Existing target is an error.
DO $guard$ BEGIN IF current_database() <> 'postgres' THEN RAISE EXCEPTION 'Wrong database: %', current_database(); END IF; IF current_setting('server_version_num')::integer NOT BETWEEN 180000 AND 189999 THEN RAISE EXCEPTION 'PostgreSQL 18 required'; END IF; END; $guard$;
CREATE DATABASE manufacturing_360_v2 WITH TEMPLATE template0 ENCODING 'UTF8';
