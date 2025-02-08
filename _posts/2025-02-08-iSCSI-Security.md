---
layout: post
title: iSCSI Applications & Security
categories: ['blog']
tags: ['cyber', 'iscsi', 'networking']
---

iSCSI (Internet Small Computer Systems Interface) is a powerful protocol that allows you to extend storage capabilities over a network. Whether you're managing a home office setup or a full-fledged data center, iSCSI can help you integrate Network Attached Storage (NAS) devices with hypervisors like VMware ESXi. However, like any network device, iSCSI present a number of security vulnerabilities and attack surfaces that must be considered.  This guide will explore the iSCSI protocol, its applications, and various security considerations to ensure your data remains protected.

## What is iSCSI?  

iSCSI is a network storage protocol that enables communication between storage devices and servers. It is literally based on the [Small Computer Systems Interface](https://datatracker.ietf.org/doc/html/rfc3783) (SCSI) which was a widespread protocol for connecting I/O devices like disk-drives.  While SCSI is still used today, it's been supplanted by [Serial ATA](https://sata-io.org/) (SATA) for most consumer usecases.  However the spirit of SCSI still lives in iSCSI, which is essentially SCSI over a network.  It works by encapsulating SCSI commands (the protocol used for local disk communication) into TCP/IP packets, allowing them to traverse standard Ethernet networks.  

### Key Features of iSCSI:  
- **Block-level Access**: Unlike file-level protocols like NFS, iSCSI provides block-level storage access, making it ideal for database servers or virtualized environments.  
- **Interoperability**: iSCSI works over existing network infrastructure, saving you from investing in expensive fiber-channel hardware.  
- **Cost-efficiency**: By leveraging Ethernet, iSCSI offers a more affordable alternative to traditional storage area networks (SANs).  

### Additional Technical Details:

  * [Internet Small Computer Systems Interface (iSCSI)](https://datatracker.ietf.org/doc/html/rfc3720), RFC, *Internet Engineering Task Force (IETC) - Network Working group*, April, 2004.
  * [Open-iscsi project](https://github.com/open-iscsi/open-iscsi) : iSCSI tools for Linux
  * [goisci](https://github.com/dell/goiscsi) :  Portable Go module for iSCSI operations, *Dell*

## Application of iSCSI :  ESXi Datastores

iSCSI is a versatile protocol that fits a variety of use cases, whether you're working in a small-scale home office or managing enterprise-grade infrastructure.  If you are using a virtualized infrastructre (e.g. VMWare ESXi), its pretty simple to use iSCSI to the hypervisor and create new datastores.

### Adding LUNs to an ESXi Hypervisor  

The process entails adding adding Logical Unit Numbers (LUNs) from a NAS device (e.g. Synology Device, ReadyNAS, FreeNAS) to an ESXi hypervisor. LUNs are essentially virtualized storage volumes that can be accessed as block devices. Here’s how it works:  

1. **Prepare the NAS Device**:  
   - Configure the NAS to act as an iSCSI target.  This is pretty simple and documented in your NAS documentation.
   - Create and allocate LUNs for use by your hypervisor.  This is accomplished via your NAS web console, and entails setting a LUN Name, specifying how much data is available on the LUN, and adding it to Groups.
   - Configure and enable CHAP security protocol as needed (Highly Recommended)
   - Ensure you note the target IP address (of the NAS) and the LUN information (a DNS-looking id) as you will need them on the Hypervisor.

2. **Configure the ESXi Hypervisor**:  
   - Navigate to **Storage Adapters** in the ESXi client and add a new iSCSI software adapter.  
   - Enter the IP address of the NAS device as the iSCSI target and add the LUN id
   - Add the CHAP security information you specified for the LUN
   - Perform a rescan to detect the available LUNs.  

3. **Mount the LUNs**:  
   - Format the LUNs with VMware’s VMFS file system.  
   - Add the newly created datastore to your ESXi environment so it can be used for virtual machine storage.  


## iSCSI Security Considerations

While iSCSI is a flexible protocol, security is a concern, especially in environments where sensitive data is stored or accessed. Without proper precautions, iSCSI connections can expose your systems to unauthorized access, data breaches, or malicious attacks. Considerations for iSCSI include Authentication, Network Segmentation, Encryption and Access Control.

While it might be tempting to say "It's all internal communication anyway," you leave your self wide open to lateral movement attacks that can find, target and exploit iSCSI.  Here are a few examples:

   * [CVE-2023-21527](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-21527) : Microsoft Windows up to Server 2022 iSCSI Service denial of service
   * [CVE-2021-3139](https://cve.mitre.org/cgi-bin/cvename.cgi?name=2021-3139) : Open-iSCSI vulnerability in tcmu-runner 1.3.x, 1.4.x, and 1.5.x through 1.5.2
   * [CVE-2020-28374](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-28374) : LIO SCSI target code can be used by remote attackers to read or write files via directory traversal 

### 1. **Authentication**  

**By default, iSCSI communication does not enforce authentication, which can be a major vulnerability**. This is the number one security concern.  To mitigate this, use the following authentication mechanisms:  

- **CHAP (Challenge-Handshake Authentication Protocol)**:  
  CHAP secures iSCSI sessions by requiring both initiators (clients) and targets (storage devices) to authenticate using a shared secret. Configure this in both your NAS device and ESXi hypervisor.  

- **Mutual CHAP**:  
  For added security, enable mutual CHAP, which requires both ends of the connection to authenticate each other.  

### 2. **Network Segmentation**  

iSCSI traffic typically runs over TCP port 3260, which can be accessible across your network unless precautions are taken. To secure your iSCSI environment:  

- **Isolate iSCSI Traffic**: Use VLANs to segment iSCSI traffic from your general network traffic.  

- **Dedicated Network Interfaces**: Assign dedicated NICs (Network Interface Cards) for iSCSI to avoid congestion and improve security.  

- **IPsec**: Protects iSCSI communication by encrypting packets at the network layer. This is especially important in environments where iSCSI traffic might traverse untrusted networks.  

### 3. **Access Control**  

Limit which devices can access your iSCSI target by implementing access control lists (ACLs) on your NAS device. This can include firewall rules that only allow iSCSI traffic from known clients that will connect to the LUN.  These lists should be configured to allow only specific IP addresses to connect to the target. 

### 4. **Monitoring and Auditing**  

Regularly monitor your iSCSI environment for unauthorized access or anomalous activity. Use logging and auditing features on both the NAS device and ESXi hypervisor to track iSCSI sessions and detect potential breaches.  

### 5. **Software Updates**  

Keep your NAS firmware, ESXi hypervisor, and underlying network infrastructure updated. Vulnerabilities in iSCSI implementations or network stacks can be exploited if left unpatched.  


## iSCSI (Lack of) Encryption

By itself, the iSCSI does not offer encryption.  This is another major security concern when using it.  Inside your firewall, this can be mitigated by using Layer 2 security controls like MAC address filtering and network segmentation (VLANs).  Outside your firewall, you should definitely use a secure VPN tunnel to wrap all iSCSI connections!