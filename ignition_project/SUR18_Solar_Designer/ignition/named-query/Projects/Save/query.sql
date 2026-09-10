INSERT INTO projects (code,name,client_name,address,latitude,longitude,timezone,status,created_by)
VALUES (:code,:name,:client_name,:address,:latitude,:longitude,:timezone,:status,:user)
ON DUPLICATE KEY UPDATE project_id=LAST_INSERT_ID(project_id), name=VALUES(name),
 client_name=VALUES(client_name), address=VALUES(address), latitude=VALUES(latitude),
 longitude=VALUES(longitude), timezone=VALUES(timezone), status=VALUES(status);
