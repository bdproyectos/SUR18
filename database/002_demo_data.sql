USE sur18_pv;
INSERT INTO projects
  (code, name, client_name, address, latitude, longitude, status, created_by)
VALUES
  ('SUR18-DEMO-001', 'Planta Andina – Cochabamba', 'Industria Andina S.R.L.',
   'Parque Industrial, Cochabamba, Bolivia', -17.3935000, -66.1570000, 'Piloto', 'sur18_demo')
ON DUPLICATE KEY UPDATE name=VALUES(name);
