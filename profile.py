"""Use this profile for experiments that involve sending packets between U280s and 100 GbE NICs.
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

imageList = [('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04')] 

toolVersion = [('2022.2'),
               ('Do not install tools')]      
                   
pc.defineParameter("toolVersion", "Tool Version",
                   portal.ParameterType.STRING,
                   toolVersion[0], toolVersion,
                   longDescription="Select a tool version.")   
pc.defineParameter("osImage", "Select Image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Supported operating systems are Ubuntu and CentOS.")  
# Optional ephemeral blockstore
pc.defineParameter("tempFileSystemSize", "Temporary Filesystem Size",
                   portal.ParameterType.INTEGER, 0,advanced=True,
                   longDescription="The size in GB of a temporary file system to mount on each of your " +
                   "nodes. Temporary means that they are deleted when your experiment is terminated. " +
                   "The images provided by the system have small root partitions, so use this option " +
                   "if you expect you will need more space to build your software packages or store " +
                   "temporary files.")
# Instead of a size, ask for all available space. 
pc.defineParameter("tempFileSystemMax",  "Temp Filesystem Max Space",
                    portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Instead of specifying a size for your temporary filesystem, " +
                    "check this box to allocate all available disk space. Leave the size above as zero.")

pc.defineParameter("tempFileSystemMount", "Temporary Filesystem Mount Point",
                   portal.ParameterType.STRING,"/mydata",advanced=True,
                   longDescription="Mount the temporary file system at this mount point; in general you " +
                   "you do not need to change this, but we provide the option just in case your software " +
                   "is finicky.")  

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
  
  #
  # Create lan of all three interfaces.
  #
  host_iface = host.addInterface()
  host_iface.component_id = "eth3"
  host_iface.addAddress(pg.IPv4Address("192.168.40." + str(i+10), "255.255.255.0"))

  lan.addInterface(host_iface)

  # Print the RSpec to the enclosing page.
  
  # Optional Blockstore
  if params.tempFileSystemSize > 0 or params.tempFileSystemMax:
    bs = host.Blockstore(name + "-bs", params.tempFileSystemMount)
    if params.tempFileSystemMax:
      bs.size = "0GB"
    else:
      bs.size = str(params.tempFileSystemSize) + "GB"
      pass
    bs.placement = "any"
    pass
  if params.toolVersion != "Do not install tools":
    host.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + params.toolVersion + " >> /local/repository/output_log.txt"))
  pass   
  # Debugging
request.skipVlans()
pc.printRequestRSpec(request)
