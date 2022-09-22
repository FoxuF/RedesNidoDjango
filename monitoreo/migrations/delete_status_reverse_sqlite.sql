CREATE TABLE monitoreo_status
(
    id          integer  NOT NULL PRIMARY KEY AUTOINCREMENT,
    alive       bool     NOT NULL,
    lastAlive   datetime NULL,
    ipDevice_id bigint   NOT NULL REFERENCES todos_los_nodos_ipdevice (id),
    list_id     bigint   NOT NULL REFERENCES monitoreo_watchlist (id)
);

INSERT INTO monitoreo_status (id, ipDevice_id, list_id, alive, lastAlive)
SELECT m2m_wi.id, m2m_wi.ipdevice_id, m2m_wi.watchlist_id, ip_d.alive, ip_d.lastAlive
FROM monitoreo_watchlist_devices m2m_wi
         LEFT JOIN todos_los_nodos_ipdevice ip_d
                   ON m2m_wi.ipdevice_id = ip_d.id;

DROP TABLE "monitoreo_watchlist_devices";