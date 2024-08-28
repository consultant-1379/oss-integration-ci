/**
* common.groovy
*
* This file contains common groovy functions used across most of Ticketmaster's Jenkins pipelines
*
*/

def stage_start_retry(stage_name, retry_attempt, timeout_length){
    /**
    Method to open a stage with retry attempts

    Input:
    stage_name: The name of the stage the function is being run in
    retry_attempt: The number of the retry attempt
    timeout_length: Time to wait on a retry of the stage before executing again
    */
    if (retry_attempt > 1) {
        echo "Rerunning the \"" + stage_name + "\" stage. Retry " + retry_attempt + " of 5. Sleeping before retry..."
        sleep(timeout_length)
    }
    else {
        echo "Running the \"" + stage_name + "\" stage. Try " + retry_attempt + " of 5"
    }
    return retry_attempt + 1
}

def command_timeout(time_and_unit, command) {
    /**
    Method to add a timeout to a command

    Input:
    time_and_unit: A string in the format <amount_of_time><unit_of_time> e.g. 5m for five minutes
    command: The shell command to run e.g. git submodule sync
    */

    def timeout_command = "timeout " + time_and_unit + " " + command
    def exit_status_of_command = sh(script: timeout_command, returnStatus: true)

    if (exit_status_of_command == 124) {
        echo 'The following command timed-out: ' + command
        // Fail the build
        sh(script: 'exit 124')
    }
}

return this
