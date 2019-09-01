const Batch = require('aws-sdk/clients/batch')
const uuid = require('uuid/v4')
const util = require('util')

const JOB_DEFINITION = "tuttofare-job"
const JOB_QUEUE = "tuttofare-queue"

const client = new Batch()

exports.handler = async (event) => {
  try {
    let params = {
      jobDefinition: JOB_DEFINITION,
      jobName: uuid(),
      jobQueue: JOB_QUEUE,
    }

    result = await client.submitJob(params).promise()
    console.log(`Started AWS Batch job ${result.jobId}`)
  } catch (error) {
    console.error(error)
    return error
  }

  return result
}
