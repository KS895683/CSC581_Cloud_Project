#!/usr/bin/env python3

import geni.portal as portal
import geni.rspec.pg as rspec

pc = portal.Context()

# Create a request for one node
request = pc.makeRequestRSpec()

# Add a single node
node = request.RawPC("node")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"

# Install Docker and Docker Compose
install_docker = rspec.Execute(
    shell="sudo apt update -y && sudo apt install -y docker.io docker-compose && sudo usermod -aG docker $USER",
    shell="bash"
)
node.addService(install_docker)

# Wait for Docker to be ready and start your stack
start_services = rspec.Execute(
    shell="cd /local/repository && docker-compose up --build -d",
    shell="bash"
)
node.addService(start_services)

pc.printRequestRSpec(request)
