const Batch = require('aws-sdk/clients/batch')
const uuid = require('uuid/v4')
const util = require('util')

const JOB_DEFINITION = "relive-job"
const JOB_QUEUE = "relive-queue"

const client = new Batch()

exports.handler = async (event) => {
  try {
    let params = {
      jobDefinition: JOB_DEFINITION,
      jobName: uuid(),
      jobQueue: JOB_QUEUE,
      parameters: {
        test: 'testparam',
        job: JSON.stringify({type: 'mytest', value: 'ciao'})
      }
    }

    result = await client.submitJob(params).promise()
    console.log(`Started AWS Batch job ${result.jobId}`)
  } catch (error) {
    console.error(error)
    return error
  }

  return result
}
