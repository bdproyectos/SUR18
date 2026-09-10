# Requiere el módulo Reporting de Ignition y el reporte Informes/Proyecto FV.

PROJECT_NAME = 'SUR18_Solar_Designer'
REPORT_PATH = 'Informes/Proyecto FV'

def filename(project_code, revision):
    return 'SUR18_%s_R%02d.pdf' % (project_code.replace(' ', '_'), int(revision))

def render_pdf(project_id, project_code, revision):
    """Genera el PDF en memoria. Usar desde Perspective o un endpoint Web Dev."""
    parameters = {'project_id': long(project_id)}
    return system.report.executeReport(
        path=REPORT_PATH,
        project=PROJECT_NAME,
        parameters=parameters,
        fileType='pdf'
    )

def download_pdf(project_id, project_code, revision):
    """Inicia la descarga en una sesión Perspective."""
    content = render_pdf(project_id, project_code, revision)
    system.perspective.download(
        data=content,
        filename=filename(project_code, revision),
        contentType='application/pdf'
    )

def save_pdf(project_id, project_code, revision, directory):
    """Gateway: use una carpeta configurada, nunca una ruta enviada por usuario."""
    settings = {'path': directory, 'fileName': filename(project_code, revision), 'format': 'pdf'}
    system.report.executeAndDistribute(
        path=REPORT_PATH, project=PROJECT_NAME, parameters={'project_id': long(project_id)},
        action='save', actionSettings=settings
    )
