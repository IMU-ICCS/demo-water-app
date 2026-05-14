
# -----------------------------------------------------------------------------
# EMS client image, used to copy needed staff

ARG EMS_CLIENT_IMAGE
FROM ${EMS_CLIENT_IMAGE:-registry.gitlab.com/nebulous-project/ems-main/ems-client:experiment} AS ems-client

# -----------------------------------------------------------------------------
# Main VM image

ARG VM_BASE_IMAGE
FROM ${VM_BASE_IMAGE:-eclipse-temurin:21.0.6_7-jre}

ARG ROOT_PASSWORD

# Add JRE to PATH
ENV JAVA_HOME="/opt/java/openjdk"
ENV PATH="$PATH:$JAVA_HOME/bin"
RUN echo "JAVA_HOME=$JAVA_HOME" >> /root/MY_VARS && \
    echo "PATH=$PATH:$JAVA_HOME/bin" >> /root/MY_VARS && \
    cat /root/MY_VARS >> /root/.bashrc


# Install Python3
RUN apt-get update && \
    apt-get install -y python3 python3-pip
# apt-get install -y python3-dev python3-venv build-essential

# Install and configure Sshd
RUN apt-get install -y openssh-server

# Configure SSH
RUN mkdir /var/run/sshd  && \
    echo "root:${ROOT_PASSWORD}" | chpasswd  && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config  && \
    sed -i 's/#PermitUserEnvironment no/PermitUserEnvironment yes/' /etc/ssh/sshd_config  && \
    rm -f /etc/ssh/ssh_host_rsa_key*  && \
    ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''  && \
    sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd && \
    cat /root/MY_VARS >> /root/.ssh/environment

# Copy EMS client here
COPY --from=ems-client  /opt/baguette-client  /root/baguette-client
RUN sed -i '/^K8S_MONITOR_ENABLED=/d' /root/baguette-client/bin/run.sh

# Cleanup
RUN rm /var/lib/apt/lists/lock /var/cache/apt/archives/lock

# Start SSH server
CMD ["/usr/sbin/sshd", "-D"]