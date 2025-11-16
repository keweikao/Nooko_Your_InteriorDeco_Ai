import { callMCPTool } from './mcp-server/client';

async function testReadCloudRunLogs() {
  const projectId = 'nooko-yourinteriordeco-ai'; // Replace with your project ID
  const serviceName = 'analysis-service';
  const revisionName = 'analysis-service-00006-64p'; // Replace with the latest failed revision name

  try {
    console.log(`Attempting to read logs for service: ${serviceName}, revision: ${revisionName}`);
    const logs = await callMCPTool('readCloudRunLogs', {
      projectId,
      serviceName,
      revisionName,
      limit: 10, // Fetch last 10 log entries
    });

    console.log('Successfully fetched logs:');
    logs.forEach((log: any) => {
      console.log(`[${log.timestamp}] [${log.severity}] ${log.message}`);
    });
  } catch (error) {
    console.error('Error testing readCloudRunLogs:', error);
  }
}

testReadCloudRunLogs();
