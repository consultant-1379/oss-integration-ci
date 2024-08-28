#!/usr/bin/env groovy

import groovy.json.JsonOutput

node {
    parameters {
        string(name: 'SPINNAKER_WEBHOOK',
                defaultValue: params.SPINNAKER_WEBHOOK ?: '',
                description: 'Webhook for the Spinnaker pipeline to trigger.' )
    }
    stage('Call Spinnaker Webhook') {
        if (params.GERRIT_HOST != '' && params.GERRIT_PORT != '' && params.GERRIT_SCHEME != '' && params.GERRIT_VERSION != '' && params.SPINNAKER_WEBHOOK != '') {
            def json = JsonOutput.toJson(params)
            def post = new URL("https://spinnaker-api.rnd.gic.ericsson.se/webhooks/webhook/" + params.SPINNAKER_WEBHOOK).openConnection()
            post.setRequestMethod("POST")
            post.setDoOutput(true)
            post.setRequestProperty("Content-Type", "application/json")
            post.getOutputStream().write(json.getBytes("UTF-8"))
            def postRC = post.getResponseCode()
            if(postRC.equals(200)) {
                println(post.getInputStream().getText())
            }
            else {
                println(postRC)
            }
        }
    }
}
