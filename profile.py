"""OCT Alveo U280 + 100 GbE NIC profile with post-boot script
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
"""fpga 
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

# Variable number of nodes.
pc.defineParameter("nodeCount", "Number of Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="Enter the number of FPGA nodes. Maximum is 16.")

# Pick your image.
imageList = [('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
             ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04')] 

toolVersion = [('2023.1'),
               ('Do not install tools')]      
                   
pc.defineParameter("toolVersion", "Tool Version",
                   portal.ParameterType.STRING,
                   toolVersion[0], toolVersion,
                   longDescription="Select a tool version. It is recommended to use the latest version for the deployment workflow. For more information, visit https://www.xilinx.com/products/boards-and-kits/alveo/u280.html#gettingStarted")   
pc.defineParameter("osImage", "Select Image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Supported operating systems are Ubuntu and CentOS.")  
# Optionally start X11 VNC server.
pc.defineParameter("startVNC",  "Start X11 VNC on your nodes",
                   portal.ParameterType.BOOLEAN, False,
                   longDescription="Start X11 VNC server on your nodes. There will be " +
                   "a menu option in the node context menu to start a browser based VNC " +
                   "client. Works really well, give it a try!")
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
                   
# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()        

# Check parameter validity.

if params.nodeCount < 1 or params.nodeCount > 4:
    pc.reportError(portal.ParameterError("The number of FPGA nodes should be greater than 1 and less than 4.", ["nodeCount"]))
    pass
  
pc.verifyParameters()

lan = request.LAN()  

# Process nodes, adding to FPGA network
for i in range(params.nodeCount):
    # Create a node and add it to the request
    name = "node" + str(i)
    node = request.RawPC(name)
    node.disk_image = params.osImage
    # Assign to the node hosting the FPGA.
    node.hardware_type = "fpga-alveo-100g"
    node.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"

    host_iface = node.addInterface()
    host_iface.component_id = "eth3"
    #host_iface.addAddress(pg.IPv4Address("192.168.40." + str(i+10), "255.255.255.0"))

    lan.addInterface(host_iface)
    
    # Optional Blockstore
    if params.tempFileSystemSize > 0 or params.tempFileSystemMax:
        bs = node.Blockstore(name + "-bs", params.tempFileSystemMount)
        if params.tempFileSystemMax:
            bs.size = "0GB"
        else:
            bs.size = str(params.tempFileSystemSize) + "GB"
            pass
        bs.placement = "any"
        pass
        #
    # Install and start X11 VNC. Calling this informs the Portal that you want a VNC
    # option in the node context menu to create a browser VNC client.
    #
    # If you prefer to start the VNC server yourself (on port 5901) then add nostart=True. 
    #
    if params.startVNC:
        node.startVNC()
        pass
    if params.toolVersion != "Do not install tools":
        node.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + params.toolVersion + " >> /local/repository/output_log.txt"))
        pass 
    pass
request.skipVlans()  
pc.printRequestRSpec(request)
