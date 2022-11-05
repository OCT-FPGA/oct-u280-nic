"""FPGA-NIC Experiment Profile
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
pc.defineParameter("FPGANodeCount", "Number of FPGA Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="Enter the number of FPGA nodes. Maximum is 4.")

pc.defineParameter("NICNodeCount", "Number of 100G NIC Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="Enter the number of 100G NIC nodes. Maximum is 4.")

# Pick your image.
imageList = [
    #('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),    
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD', 'UBUNTU 18.04'), 
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU16-64-STD', 'UBUNTU 16.04'),
    #('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS8-64-STD', 'CENTOS 8.4'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS7-64-STD', 'CENTOS 7.9')] 

toolVersion = [#('2022.1'),
               ('2021.1'), 
               ('2020.2.1'), 
               ('2020.2'), 
               ('2020.1.1'),
               ('2020.1'),
               ('Do not install tools')]      
                   
pc.defineParameter("toolVersion", "Tool Version",
                   portal.ParameterType.STRING,
                   toolVersion[0], toolVersion,
                   longDescription="Select a tool version. It is recommended to use the latest version for the deployment workflow. For more information, visit https://www.xilinx.com/products/boards-and-kits/alveo/u280.html#gettingStarted")   
pc.defineParameter("osImage", "Select Image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Supported operating systems are Ubuntu and CentOS.")                    
                   
# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()        

# Check parameter validity.

if params.FPGANodeCount < 1 or params.FPGANodeCount > 4:
    pc.reportError(portal.ParameterError("The number of FPGA nodes should be greater than 1 and less than 4.", ["FPGANodeCount"]))
    pass
if params.NICNodeCount < 1 or params.NICNodeCount > 4:
    pc.reportError(portal.ParameterError("The number of NIC nodes should be greater than 1 and less than 4.", ["NICNodeCount"]))
    pass  
if params.osImage == "urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS8-64-STD" and params.toolVersion == "2020.1":
    pc.reportError(portal.ParameterError("OS and tool version mismatch.", ["osImage"]))
    pass
  
pc.verifyParameters()

# lan = request.LAN()
# Create link/lan.
if params.NICNodeCount > 1:
    if params.NICNodeCount == 2:
        lan = request.Link()
    else:
        lan = request.LAN()
        pass
    #if params.bestEffort:
    #    lan.best_effort = True
    #elif params.linkSpeed > 0:
    #    lan.bandwidth = params.linkSpeed
    #if params.sameSwitch:
    #    lan.setNoInterSwitchLinks()
    pass

# Process nodes, adding to FPGA network
for i in range(params.FPGANodeCount):
    # Create a node and add it to the request
    name = "node" + str(i)
    node = request.RawPC(name)
    node.disk_image = params.osImage
    # Assign to the node hosting the FPGA.
    node.hardware_type = "fpga-alveo"
    node.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"
    
    if params.toolVersion != "Do not install tools":
        node.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + params.toolVersion + " >> /local/repository/output_log.txt"))
        pass 
    pass
pc.printRequestRSpec(request)

# Process nodes, adding to 100G NIC network
for i in range(params.NICNodeCount):
    # Create a node and add it to the request
    name = "node" + str(i)
    node = request.RawPC(name)
    node.disk_image = params.osImage
    # Assign to the node hosting the FPGA.
    node.hardware_type = "fpga-alveo-100g"
    node.component_manager_id = "urn:publicid:IDN+cloudlab.umass.edu+authority+cm"

    # Add to lan
    if params.NICNodeCount > 1:
        iface = node.addInterface("eth1")
        lan.addInterface(iface)
        pass
    
    if params.toolVersion != "Do not install tools":
        node.addService(pg.Execute(shell="bash", command="sudo /local/repository/post-boot.sh " + params.toolVersion + " >> /local/repository/output_log.txt"))
        pass 
    pass
pc.printRequestRSpec(request)
