"""A profile that requests a 100G NIC and a U280 FPGA.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
"""A profile that requests a 100G NIC and a U280 FPGA.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# We use the URN library below.
import geni.urn as urn
# Emulab extension
import geni.rspec.emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

pc.defineParameter("nodeCount", "Number of Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="Enter the number of FPGA/NIC nodes. Maximum is 4.")

params = pc.bindParameters() 

if params.nodeCount < 1 or params.nodeCount > 4:
    pc.reportError(portal.ParameterError("The number of FPGA nodes should be greater than 1 and less than 4.", ["nodeCount"]))
    pass
  
lan = request.LAN()  

# Add a PC to the request.
for i in range(params.nodeCount):
  name = "host" + str(i)
  host = request.RawPC(name)
  # UMass cluster
  host.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
  # Assign to the node hosting the FPGA.
  host.hardware_type = "fpga-alveo-100g"
  # Use the default image for the type of the node selected. 
  host.setUseTypeDefaultImage()

  #
  # Create lan of all three interfaces.
  #
  host_iface = host.addInterface()
  host_iface.component_id = "eth3"
  host_iface.addAddress(pg.IPv4Address("192.168.40." + str(i+10), "255.255.255.0"))

  lan.addInterface(host_iface)

  # Print the RSpec to the enclosing page.

  host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + "2021.1" + " >> /local/repository/output_log.txt"))

  # Debugging
request.skipVlans()
pc.printRequestRSpec(request)
