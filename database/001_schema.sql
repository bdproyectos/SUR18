CREATE DATABASE IF NOT EXISTS sur18_pv
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sur18_pv;

CREATE TABLE IF NOT EXISTS projects (
    project_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(160) NOT NULL,
    client_name VARCHAR(160) NOT NULL,
    address TEXT,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    timezone VARCHAR(64) NOT NULL DEFAULT 'America/La_Paz',
    status VARCHAR(24) NOT NULL DEFAULT 'Borrador',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(120) NOT NULL,
    CONSTRAINT projects_latitude_chk CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT projects_longitude_chk CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE IF NOT EXISTS designs (
    design_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    project_id BIGINT NOT NULL,
    revision INT NOT NULL,
    name VARCHAR(160) NOT NULL,
    input_json JSON NOT NULL,
    result_json JSON NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(120) NOT NULL,
    CONSTRAINT designs_project_fk FOREIGN KEY (project_id)
        REFERENCES projects(project_id) ON DELETE CASCADE,
    CONSTRAINT designs_project_revision_uk UNIQUE(project_id, revision)
);

CREATE INDEX designs_project_created_idx ON designs(project_id, created_at DESC);
