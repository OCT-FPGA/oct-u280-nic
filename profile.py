"""An example of constructing a profile that requests the FPGA commbo.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
"""An example of constructing a profile that requests the FPGA commbo.
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

# Add a PC to the request.
host = request.RawPC("host")
# UMass cluster
host.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
# Assign to the node hosting the FPGA.
host.component_id = "pc162"
# Use the default image for the type of the node selected. 
host.setUseTypeDefaultImage()

# Since we want to create network links to the FPGA, it has its own identity.
fpga = request.RawPC("fpga")
# UMass cluster
fpga.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
# Assign to the fgpa node
fpga.component_id = "fpga-pc162"
# Use the default image for the type of the node selected. 
fpga.setUseTypeDefaultImage()

# Secret sauce.
fpga.SubNodeOf(host)

#
# Create lan of all three interfaces.
#
#host_iface1 = host.addInterface()
#host_iface1.component_id = "eth2"
#host_iface1.addAddress(pg.IPv4Address("192.168.40.3", "255.255.255.0"))
host_iface2 = host.addInterface()
host_iface2.component_id = "eth3"
host_iface2.addAddress(pg.IPv4Address("192.168.40.6", "255.255.255.0"))
fpga_iface1 = fpga.addInterface()
fpga_iface1.component_id = "eth0"
fpga_iface1.addAddress(pg.IPv4Address("192.168.40.1", "255.255.255.0"))
#fpga_iface2 = fpga.addInterface()
#fpga_iface2.component_id = "eth1"
#fpga_iface2.addAddress(pg.IPv4Address("192.168.40.3", "255.255.255.0"))

lan = request.LAN()
#lan.addInterface(host_iface1)
lan.addInterface(host_iface2)
lan.addInterface(fpga_iface1)
#lan.addInterface(fpga_iface2)

# Debugging
request.skipVlans()

# Print the RSpec to the enclosing page.

host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + "2021.1" + " >> /local/repository/output_log.txt"))

pc.printRequestRSpec(request)
