SELECT design_id, revision, name,
 JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.dc_kwp')) AS dc_kwp,
 JSON_UNQUOTE(JSON_EXTRACT(result_json, '$.annual_energy_kwh')) AS annual_energy_kwh,
 created_at, created_by FROM designs WHERE project_id=:project_id ORDER BY revision DESC;
