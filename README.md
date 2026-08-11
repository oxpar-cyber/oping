# oping
# oping
# Python ICMP Ping Utility

## Overview

A feature-rich network diagnostic tool written in Python that sends ICMP Echo Request packets to target hosts using raw sockets. Displays detailed statistics including round-trip times, packet loss, and color-coded output for easy visual assessment.

**Version:** 1.0  
**Author:** Joris Schot  
**License:** For educational purposes

---

## Features

- ✅ **Raw ICMP Sockets** - Direct access to ICMP protocol level
- ✅ **Color-Coded Output** - Visual RTT indication (green/yellow/red)
- ✅ **Packet Loss Tracking** - Real-time percentage calculation
- ✅ **Detailed Statistics** - Min/Max/Average RTT + Standard Deviation
- ✅ **Count Mode** - Send a specific number of pings
- ✅ **Continuous Mode** - Run indefinitely until manually stopped
- ✅ **Configurable Timeout** - Adjustable per-packet timeout value
- ✅ **Cross-Platform Compatible** - Works on Linux, macOS, Windows (admin required)
- ✅ **Clean CLI Interface** - Built-in argument parsing with help

---

## Requirements

### Software Dependencies

- Python 3.6 or higher
- No external packages required (uses standard library only)

### System Permissions

⚠️ **Admin/root privileges ARE REQUIRED** because raw socket access requires elevated permissions.

| Platform | Command |
|----------|---------|
| Linux/macOS | `sudo python3 ping.py <target>` |
| Windows | Run terminal as Administrator |

---

## Installation

1. Save the script as `ping.py`:

```bash
nano ping.py    # or any editor you prefer
Make executable (Linux/macOS):

chmod +x ping.py

Test installation:

python3 --version
sudo python3 ping.py --help

Usage
Basic Syntax

sudo python3 ping.py [OPTIONS] <IP-address-or-hostname>

Command Line Arguments
Argument	Short	Description	Default
<target>	(positional)	Target IP address or hostname	Required
--count	-c	Number of echo requests to send	4
--timeout	-t	Timeout per packet in seconds	2.0
--continuous	(none)	Ping continuously until Ctrl+C	False
--no-color	(none)	Disable color output	False
--help	-h	Show help message and exit	-

Usage Examples
Example 1: Quick Connectivity Test

sudo python3 ping.py 8.8.8.8
Pings Google DNS 4 times with default settings.

Example 2: Custom Packet Count

sudo python3 ping.py google.com -c 10
Sends exactly 10 ping requests to google.com.

Example 3: Continuous Monitoring

sudo python3 ping.py 192.168.1.1 --continuous
Runs infinitely until you press Ctrl+C. Useful for detecting intermittent connectivity issues.

Example 4: Increased Timeout

sudo python3 ping.py slow-server.local -t 5
Useful for targets with high latency or unreliable connections.

Example 5: No Color Output (for logging)

sudo python3 ping.py example.org --no-color > results.txt
Redirects plain-text output to a file for analysis or record keeping.

Output Explanation
Sample Console Output
Pinging 8.8.8.8 (4 times) with 32 bytes of data:

  1: Reply from 8.8.8.8: bytes=32 time=12.45ms TTL=64
  2: Reply from 8.8.8.8: bytes=32 time=11.82ms TTL=64
  3: Request timed out
  4: Reply from 8.8.8.8: bytes=32 time=13.01ms TTL=64

───────────────────────────────────────────────────────
Ping statistics for 8.8.8.8:
───────────────────────────────────────────────────────
    Packets: sent = 4, received = 3, lost = 1 (25.0% loss)
    Round-trip times (ms):
        Minimum       = 11.82ms
        Maximum       = 13.01ms
        Average       = 12.43ms
        Std deviation = 0.49ms
───────────────────────────────────────────────────────
Field Descriptions
Field	Description
Sequence (#)	Incrementing counter showing which packet
Destination	The resolved IP address of the target
Bytes	Payload size (fixed at 32 bytes)
Time	Round-trip time (RTT) in milliseconds
TTL	Time-To-Live (hops remaining before packet expires)

Color Coding Legend
Per-Ping Response Colors
Color	RTT Range	Status
🟢 Green	< 50ms	Excellent
🟡 Yellow	50–150ms	Acceptable
🔴 Red	≥ 150ms	Poor

Packet Loss Colors
Color	Loss Percentage	Status
🟢 Green	0%	Perfect
🟡 Yellow	< 25%	Some issues
🔴 Red	≥ 25%	Significant problems

Internal Mechanics
ICMP Protocol Details
Type: 8 (Echo Request) / 0 (Echo Reply)
Checksum: Calculated manually per RFC 792
Identifier: Fixed packet ID (0x1234)
Sequence Number: Increments each request
Socket Configuration

socket.AF_INET      # IPv4 family
socket.SOCK_RAW     # Raw socket
socket.IPPROTO_ICMP # ICMP protocol

Troubleshooting
Issue: Permission Denied / Access Denied
Cause: Missing admin/root privileges

Solution:
# Linux/macOS
sudo python3 ping.py 8.8.8.8

# Windows PowerShell (Run as Administrator)
python ping.py 8.8.8.8
Issue: Could Not Resolve Host
Cause: Invalid hostname or DNS failure

Solution: Use IP addresses directly or check /etc/resolv.conf configuration.


sudo python3 ping.py 192.168.1.1   # Try numeric IP instead
Issue: All Requests Timed Out
Possible Causes:

Firewall blocking ICMP Echo Replies
Target host configured not to respond to pings
Network routing issue
High latency exceeding timeout threshold
Solutions:

Increase timeout: -t 5 or longer
Check firewall rules on both ends
Verify physical network connectivity
Try alternate target to isolate problem

Issue: Colored Output Garbled (Windows CMD)
Cause: Terminal doesn't support ANSI escape sequences

Solution:
# Option A: Use WSL (Windows Subsystem for Linux)
# Option B: Use PowerShell
# Option C: Disable colors with --no-color flag
sudo python3 ping.py 8.8.8.8 --no-color

Issue: Segmentation Fault (Linux)
Cause: Rare kernel-level issue with raw sockets

Solution: Update kernel, or try alternative networking stack. Consider using standard ping command instead.

Advanced Configuration
Modify Source Code Options
Parameter	Location	Default	Adjust To
Timeout Duration	ping() function param	2.0 seconds	Longer for distant servers
Packet Size	build_icmp_packet()	32 bytes	Change data string length
Packet ID	packet_id = 0x1234	Hex constant	Unique identifier if running multiple instances
RTT Thresholds	get_color()	<50/<150 ms	Customize color thresholds
Integration with Scripts
Capture output programmatically:


import subprocess

result = subprocess.run(
    ['sudo', 'python3', 'ping.py', '-c', '5', '--no-color', 'google.com'],
    capture_output=True, text=True
)

print(result.stdout)
Limitations
Limitation	Detail
IPv6 Support	❌ Currently supports IPv4 only
ICMP Type 8 Only	❌ Cannot send other ICMP types
Privilege Required	⚠️ Requires admin access on all platforms
Single Target	❌ Must run separately for multiple IPs
No Traceroute	ℹ️ Separate tool needed for hop-by-hop path
Comparison with System ping
Feature	This Script	System ping
Language	Python	Native binary
Cross-platform	Yes (with adjustments)	Varies by OS
Raw socket control	Full control	Abstraction layer
Color output	✅ Built-in	Depends on OS version
Educational value	High (readable code)	Low (black box)
Flexibility	Easy to modify	Limited customization
Contributing Ideas
Potential enhancements you could implement:

 IPv6 support (socket.AF_INET6)
 Traceroute functionality
 CSV/JSON export options
 Periodic snapshots to database
 Graphical plotting of RTT trends
 Batch ping multiple hosts concurrently
 Proxy/tunnel support
Security Notes
⚠️ Important Considerations:

Running raw socket applications may trigger security software alerts
Frequent pinging could be interpreted as reconnaissance activity
Ensure you have authorization before scanning unfamiliar networks
Log files may contain sensitive network topology information
Legal Disclaimer
This tool is intended for educational and legitimate network administration purposes. Users are responsible for ensuring compliance with applicable laws and obtaining proper authorization before scanning networks they do not own or manage.

Changelog
Version	Date	Changes
1.0	Initial Release	Core ping functionality, stats, colors
1.1	Future	Added continuous mode
1.2	Future	Added no-color option

Support & Feedback
For bugs, questions, or suggestions:

Review troubleshooting section above first
Check Python and system permissions
Verify network connectivity independently

References
RFC 792 - Internet Control Message Protocol
Python socket module
ICMP Protocol Explained

Author's Note
This utility demonstrates practical application of raw sockets and network protocols in Python. While convenient, production environments should consider mature tools like ping, nping, or commercial network monitoring solutions for critical infrastructure.
