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
  host = request.RawPC("host")
  # UMass cluster
  host.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
  # Assign to the node hosting the FPGA.
  #host.component_id = "pc162"
  host.hardware_type = "fpga-alveo-100g"
  # Use the default image for the type of the node selected. 
  host.setUseTypeDefaultImage()

  # Since we want to create network links to the FPGA, it has its own identity.
  #fpga = request.RawPC("fpga")
  # UMass cluster
  #fpga.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
  # Assign to the fgpa node
  #fpga.component_id = "fpga-pc162"
  # Use the default image for the type of the node selected. 
  #fpga.setUseTypeDefaultImage()
  # Secret sauce.
  #fpga.SubNodeOf(host)

  #
  # Create lan of all three interfaces.
  #
  #host_iface1 = host.addInterface()
  #host_iface1.component_id = "eth2"
  #host_iface1.addAddress(pg.IPv4Address("192.168.40.3", "255.255.255.0"))
  host_iface = host.addInterface()
  host_iface.component_id = "eth3"
  host_iface.addAddress(pg.IPv4Address("192.168.40." + str(i+10), "255.255.255.0"))
  #fpga_iface1 = fpga.addInterface()
  #fpga_iface1.component_id = "eth0"
  #fpga_iface1.addAddress(pg.IPv4Address("192.168.40.1", "255.255.255.0"))
  #fpga_iface2 = fpga.addInterface()
  #fpga_iface2.component_id = "eth1"
  #fpga_iface2.addAddress(pg.IPv4Address("192.168.40.3", "255.255.255.0"))

  #lan = request.LAN()
  #lan.addInterface(host_iface1)
  lan.addInterface(host_iface)
  #lan.addInterface(fpga_iface1)
  #lan.addInterface(fpga_iface2)


  # Print the RSpec to the enclosing page.

  host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + "2021.1" + " >> /local/repository/output_log.txt"))

  # Debugging
#request.skipVlans()
pc.printRequestRSpec(request)
