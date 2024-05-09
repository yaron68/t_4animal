# Use the official Jenkins LTS image from Docker Hub
FROM jenkins/jenkins:lts

# Skip the initial setup wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Install plugins: Configuration as Code and any others you might need
RUN /usr/local/bin/install-plugins.sh configuration-as-code

# Copy your Configuration as Code YAML file into the container
COPY jenkins.yaml /var/jenkins_home/jenkins.yaml

# Copy the Groovy init script to automatically trigger the job
COPY triggerJob.groovy /usr/share/jenkins/ref/init.groovy.d/triggerJob.groovy

# Tell Jenkins where to find the Configuration as Code YAML file
ENV CASC_JENKINS_CONFIG /var/jenkins_home/jenkins.yaml

# Expose the default Jenkins port
EXPOSE 8080
EXPOSE 50000

# Set the default command to run Jenkins
CMD ["jenkins.sh"]
