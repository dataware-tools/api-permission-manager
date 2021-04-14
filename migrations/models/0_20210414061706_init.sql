-- upgrade --
CREATE TABLE IF NOT EXISTS "rolemodel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "permissions" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "usermodel" (
    "id" VARCHAR(255) NOT NULL  PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "user_role" (
    "usermodel_id" VARCHAR(255) NOT NULL REFERENCES "usermodel" ("id") ON DELETE CASCADE,
    "rolemodel_id" INT NOT NULL REFERENCES "rolemodel" ("id") ON DELETE CASCADE
);
