-- grant required permissions to the roles in the database to config_sch schema
GRANT USAGE ON SCHEMA config_sch TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA config_sch TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA config_sch TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA config_sch TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA config_sch GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA config_sch GRANT ALL ON ROUTINES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA config_sch GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;