SELECT p.project_id, p.code, p.name, p.client_name, p.latitude, p.longitude,
       p.status, p.updated_at,
       (SELECT MAX(d.revision) FROM designs d WHERE d.project_id = p.project_id) AS last_revision
FROM projects p
ORDER BY p.updated_at DESC;
