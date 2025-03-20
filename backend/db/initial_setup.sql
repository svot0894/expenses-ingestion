CREATE SCHEMA IF NOT EXISTS "config_sch";
CREATE SCHEMA IF NOT EXISTS "b_sch";
CREATE SCHEMA IF NOT EXISTS "s_sch";
CREATE SCHEMA IF NOT EXISTS "g_sch";

CREATE TABLE "config_sch"."cfg_t_file_status"(
    "file_status_id" INTEGER NOT NULL PRIMARY KEY,
    "file_status_name" VARCHAR(255) NOT NULL UNIQUE,
    "description" TEXT NULL,
    CONSTRAINT "unique_file_status_name" UNIQUE("file_status_name")
);

CREATE TABLE "config_sch"."cfg_t_files"(
    "file_id" UUID NOT NULL PRIMARY KEY,
    "file_name" VARCHAR(255) NOT NULL,
    "file_size" INTEGER NOT NULL,
    "number_rows" INTEGER NOT NULL,
    "checksum" VARCHAR(255) NOT NULL,
    "file_status_id" INTEGER NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT '1',
    "error_message" TEXT NULL,
    "inserted_datetime" DATE NOT NULL DEFAULT NOW(),
    "ingested_datetime" DATE NULL,
    CONSTRAINT "unique_file_checksum" UNIQUE("checksum"),
    CONSTRAINT "fk_file_status" FOREIGN KEY ("file_status_id") REFERENCES "config_sch"."cfg_t_file_status"("file_status_id")
);

CREATE TABLE "b_sch"."b_t_expenses"(
    "b_expenses_id" UUID NOT NULL PRIMARY KEY,
    "file_id" UUID NOT NULL,
    "raw_expenses_data" TEXT NULL,
    "transaction_date" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "amount" VARCHAR(255) NOT NULL,
    "is_ingested" BOOLEAN NOT NULL DEFAULT '0',
    "inserted_datetime" DATE NOT NULL DEFAULT NOW(),
    CONSTRAINT "fk_b_file" FOREIGN KEY ("file_id") REFERENCES "config_sch"."cfg_t_files"("file_id")
);

CREATE TABLE "s_sch"."s_t_expenses"(
    "s_expenses_id" UUID NOT NULL PRIMARY KEY,
    "file_id" UUID NOT NULL,
    "transaction_date" DATE NOT NULL,
    "description" TEXT NOT NULL,
    "amount" FLOAT(10) NOT NULL,
    "is_ingested" BOOLEAN NOT NULL DEFAULT '0',
    "inserted_datetime" DATE NOT NULL DEFAULT NOW(),
    CONSTRAINT "fk_s_file" FOREIGN KEY ("file_id") REFERENCES "config_sch"."cfg_t_files"("file_id")
);

CREATE TABLE "s_sch"."s_t_expenses_error"(
    "s_error_id" UUID NOT NULL PRIMARY KEY,
    "file_id" UUID NOT NULL,
    "transaction_date" VARCHAR(255) NULL,
    "description" TEXT NULL,
    "amount" VARCHAR(255) NULL,
    "error_message" TEXT NOT NULL,
    "ready_for_reload" BOOLEAN NOT NULL DEFAULT '0',
    "inserted_datetime" DATE NOT NULL DEFAULT NOW(),
    CONSTRAINT "fk_s_error_file" FOREIGN KEY ("file_id") REFERENCES "config_sch"."cfg_t_files"("file_id")
);

CREATE TABLE "g_sch"."g_t_expenses"(
    "g_expenses_id" UUID NOT NULL PRIMARY KEY,
    "file_id" UUID NOT NULL,
    "transaction_date" DATE NOT NULL,
    "description" TEXT NOT NULL,
    "amount" FLOAT(10) NOT NULL,
    "category" VARCHAR(255) NOT NULL,
    "inserted_datetime" DATE NOT NULL DEFAULT NOW(),
    CONSTRAINT "fk_g_file" FOREIGN KEY ("file_id") REFERENCES "config_sch"."cfg_t_files"("file_id")
);