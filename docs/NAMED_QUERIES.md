# Named Queries requeridas

Configure todas con la conexión JDBC MySQL `SUR18_PV` (base `sur18_pv`) y con tipo de consulta **Prepared Statement**.

## `Projects/List`
```sql
SELECT p.project_id, p.code, p.name, p.client_name, p.latitude, p.longitude,
       p.status, p.updated_at,
       (SELECT MAX(d.revision) FROM designs d WHERE d.project_id = p.project_id) AS last_revision
FROM projects p
ORDER BY p.updated_at DESC;
```

## `Projects/Save`
Parámetros: `code`, `name`, `client_name`, `address`, `latitude`, `longitude`, `timezone`, `status`, `user`.
```sql
INSERT INTO projects (code,name,client_name,address,latitude,longitude,timezone,status,created_by)
VALUES (:code,:name,:client_name,:address,:latitude,:longitude,:timezone,:status,:user)
ON DUPLICATE KEY UPDATE
 project_id=LAST_INSERT_ID(project_id), name=VALUES(name), client_name=VALUES(client_name),
 address=VALUES(address), latitude=VALUES(latitude), longitude=VALUES(longitude),
 timezone=VALUES(timezone), status=VALUES(status);
```
Después de ejecutarla use `SELECT LAST_INSERT_ID() AS project_id` en una Named Query separada, o recupere el registro por `code`.

## `Designs/NextRevision`
Parámetro: `project_id` (Long).
```sql
SELECT COALESCE(MAX(revision),0)+1 AS revision FROM designs WHERE project_id=:project_id;
```

## `Designs/Save`
Parámetros: `project_id`, `revision`, `name`, `input_json`, `result_json`, `notes`, `user`.
```sql
INSERT INTO designs(project_id,revision,name,input_json,result_json,notes,created_by)
VALUES (:project_id,:revision,:name,CAST(:input_json AS JSON),CAST(:result_json AS JSON),:notes,:user);
```
Configure esta Named Query para devolver la clave generada, si su versión de Gateway/JDBC lo permite.

## `Designs/ListByProject`
```sql
SELECT design_id, revision, name, JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.dc_kwp')) AS dc_kwp,
       JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.annual_energy_kwh')) AS annual_energy_kwh,
       created_at, created_by
FROM designs WHERE project_id=:project_id ORDER BY revision DESC;
```
