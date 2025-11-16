import { Logging } from '@google-cloud/logging';

interface ReadCloudRunLogsInput {
  projectId: string;
  serviceName: string;
  revisionName?: string;
  filter?: string;
  limit?: number;
}

interface LogEntry {
  timestamp: string;
  severity: string;
  message: string;
  resourceType: string;
  resourceLabels: { [key: string]: string };
  [key: string]: any; // Allow other properties
}

const logging = new Logging();

export async function readCloudRunLogs(
  input: ReadCloudRunLogsInput
): Promise<LogEntry[]> {
  const { projectId, serviceName, revisionName, filter, limit = 100 } = input;

  let filterString = `resource.type="cloud_run_revision"
resource.labels.service_name="${serviceName}"
project="${projectId}"`;

  if (revisionName) {
    filterString += `
resource.labels.revision_name="${revisionName}"`;
  }

  if (filter) {
    filterString += `
${filter}`;
  }

  const [entries] = await logging.getEntries({
    filter: filterString,
    pageSize: limit,
    orderBy: 'timestamp desc',
  });

  return entries.map((entry) => {
    const { timestamp, severity, resource, ...rest } = entry;
    const message = entry.data ? (typeof entry.data === 'string' ? entry.data : JSON.stringify(entry.data)) : entry.textPayload || entry.jsonPayload || '';

    return {
      timestamp: timestamp ? new Date(timestamp.seconds * 1000).toISOString() : 'N/A',
      severity: severity || 'DEFAULT',
      message: message.trim(),
      resourceType: resource?.type || 'N/A',
      resourceLabels: resource?.labels || {},
      ...rest,
    };
  });
}
