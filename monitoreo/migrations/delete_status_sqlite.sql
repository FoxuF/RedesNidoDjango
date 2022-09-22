CREATE TABLE "monitoreo_watchlist_devices"
(
    "id"           integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "watchlist_id" bigint  NOT NULL REFERENCES "monitoreo_watchlist" ("id") DEFERRABLE INITIALLY DEFERRED,
    "ipdevice_id"  bigint  NOT NULL REFERENCES "todos_los_nodos_ipdevice" ("id") DEFERRABLE INITIALLY DEFERRED
);

INSERT INTO "monitoreo_watchlist_devices" ("id", "watchlist_id", "ipdevice_id")
SELECT "id", "list_id", "ipDevice_id"
FROM "monitoreo_status";

DROP TABLE "monitoreo_status";