CREATE TABLE `monitoreo_status`
(
    `id`          bigint     NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `alive`       TINYINT(1) NOT NULL,
    `lastAlive`   datetime(6) DEFAULT NULL,
    `ipDevice_id` bigint     NOT NULL,
    `list_id`     bigint     NOT NULL,
    FOREIGN KEY (`ipDevice_id`) REFERENCES `todos_los_nodos_ipdevice` (`id`),
    FOREIGN KEY (`list_id`) REFERENCES `monitoreo_watchlist` (`id`)
);

INSERT
INTO monitoreo_status (id, ipDevice_id, list_id, alive, lastAlive)
SELECT m2m_wlip.id, m2m_wlip.ipdevice_id, m2m_wlip.watchlist_id, ip_d.alive, ip_d.lastAlive
FROM monitoreo_watchlist_devices m2m_wlip
         LEFT JOIN todos_los_nodos_ipdevice ip_d
                   ON
                       m2m_wlip.ipdevice_id = ip_d.id;

DROP TABLE monitoreo_watchlist_devices;