import jenkins.model.*
import hudson.model.*

// Delayed job trigger to ensure Jenkins is fully up
Jenkins.instance.scheduleToRunAfterInit({
    def job = Jenkins.instance.getItemByFullName("4danimals", Job.class)
    if (job != null) {
        job.scheduleBuild(new Cause.UserIdCause())
    } else {
        println("Job not found")
    }
})
