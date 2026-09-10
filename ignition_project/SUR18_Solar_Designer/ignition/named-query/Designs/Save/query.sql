INSERT INTO designs(project_id,revision,name,input_json,result_json,notes,created_by)
VALUES (:project_id,:revision,:name,CAST(:input_json AS JSON),CAST(:result_json AS JSON),:notes,:user);
