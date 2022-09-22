CREATE TABLE `monitoreo_watchlist_devices`
(
    `id`           integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `watchlist_id` bigint                 NOT NULL,
    `ipdevice_id`  bigint                 NOT NULL,
    FOREIGN KEY (`watchlist_id`) REFERENCES `monitoreo_watchlist` (`id`),
    FOREIGN KEY (`ipdevice_id`) REFERENCES `todos_los_nodos_ipdevice` (`id`)
);

INSERT INTO `monitoreo_watchlist_devices` (`id`, `watchlist_id`, `ipdevice_id`)
SELECT `id`, `list_id`, `ipDevice_id`
FROM `monitoreo_status`;

DROP TABLE `monitoreo_status`;