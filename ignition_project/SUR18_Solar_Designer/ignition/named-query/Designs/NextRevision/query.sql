SELECT COALESCE(MAX(revision),0)+1 AS revision FROM designs WHERE project_id=:project_id;
