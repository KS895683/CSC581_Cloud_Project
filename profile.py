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
    shell="bash",
    command="sudo apt update -y && sudo apt install -y docker.io docker-compose"
)
node.addService(install_docker)

# Add the logged-in user to docker group (using $USER variable)
add_to_docker = rspec.Execute(
    shell="bash",
    command="sudo usermod -aG docker $USER"
)
node.addService(add_to_docker)

# Start Docker service
start_docker = rspec.Execute(
    shell="bash",
    command="sudo systemctl start docker && sudo systemctl enable docker"
)
node.addService(start_docker)

# Build and start the Docker stack (using sudo for permission)
start_stack = rspec.Execute(
    shell="bash",
    command="cd /local/repository && sudo docker-compose up --build -d"
)
node.addService(start_stack)

pc.printRequestRSpec(request)