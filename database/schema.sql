BEGIN;
CREATE TABLE "User" (
  "id" serial PRIMARY KEY,
  "first_name" varchar(40),
  "last_name" varchar(40),
  "zip_code" integer,
  "household_id" integer,
  "email" varchar(100),
  "phone_number" varchar(15),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "FoodItem" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "category" varchar(50),
  "user_id" integer,
  "inventory_id" integer,
  "storage_type" varchar(50),
  "expiration_date" timestamp,
  "date_opened" timestamp,
  "date_frozen" timestamp,
  "date_purchased" timestamp,
  "isMeal" boolean,
  "date_refridgerated" timestamp,
  "amount" integer,
  "unit" varchar(10),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "FoodPrice" (
  "id" serial PRIMARY KEY,
  "food_item_id" integer,
  "unit_type" varchar(10),
  "price" integer,
  "zip_code" integer,
  "source" varchar(100),
  "price_per_unit" decimal(10,2),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "UnitConversion" (
  "id" serial PRIMARY KEY,
  "unit_type_from" varchar(20),
  "unit_type_to" varchar(20),
  "conversion_factor" integer,
  "standard_unit_conversion" varchar(10)
);

CREATE TABLE "Inventory" (
  "id" serial PRIMARY KEY,
  "household_id" integer,
  "name" varchar(100),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "UserInventory" (
  "user_id" integer,
  "inventory_id" integer,
  PRIMARY KEY ("user_id", "inventory_id")
);

CREATE TABLE "Household" (
  "id" serial PRIMARY KEY,
  "name" varchar(100),
  "created_at" timestamp DEFAULT (now()),
  "updated_at" timestamp DEFAULT (now())
);

ALTER TABLE "FoodItem" ADD FOREIGN KEY ("user_id") REFERENCES "User" ("id");

ALTER TABLE "User" ADD FOREIGN KEY ("household_id") REFERENCES "Household" ("id");

ALTER TABLE "FoodPrice" ADD FOREIGN KEY ("food_item_id") REFERENCES "FoodItem" ("id");

ALTER TABLE "FoodItem" ADD FOREIGN KEY ("inventory_id") REFERENCES "Inventory" ("id");

ALTER TABLE "Inventory" ADD FOREIGN KEY ("household_id") REFERENCES "Household" ("id");

ALTER TABLE "UserInventory" ADD FOREIGN KEY ("user_id") REFERENCES "User" ("id");

ALTER TABLE "UserInventory" ADD FOREIGN KEY ("inventory_id") REFERENCES "Inventory" ("id");

COMMIT;