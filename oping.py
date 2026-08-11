import socket
import struct
import sys
import argparse
import time
import select
import signal


# --- Color codes ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def get_color(rtt):
    """Returns color based on RTT value."""
    if rtt < 50:
        return Colors.GREEN
    elif rtt < 150:
        return Colors.YELLOW
    else:
        return Colors.RED


def get_loss_color(loss_pct):
    """Returns color based on packet loss percentage."""
    if loss_pct == 0:
        return Colors.GREEN
    elif loss_pct < 25:
        return Colors.YELLOW
    else:
        return Colors.RED


def calculate_checksum(data):
    """Calculates the ICMP checksum."""
    if len(data) % 2:
        data += b'\x00'

    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)

    return ~checksum & 0xFFFF


def build_icmp_packet(packet_id, sequence):
    """Builds an ICMP Echo Request packet."""
    icmp_type = 8
    code = 0
    checksum = 0

    header = struct.pack('!BBHHH', icmp_type, code, checksum, packet_id, sequence)
    data = b'Hello, Ping!'

    checksum = calculate_checksum(header + data)
    header = struct.pack('!BBHHH', icmp_type, code, checksum, packet_id, sequence)

    return header + data


def ping(host, timeout=2, count=None, continuous=False, no_color=False):
    """Sends ICMP Echo Requests and displays statistics with color coding."""
    try:
        dest_addr = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"{Colors.RED}Error: Could not resolve '{host}'.{Colors.RESET}")
        return

    mode_msg = "continuous" if continuous else f"{count} times"
    print(f"{Colors.BOLD}{Colors.CYAN}Pinging {dest_addr} ({mode_msg}) "
          f"with 32 bytes of data:{Colors.RESET}\n")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print(f"{Colors.RED}Error: This script requires admin/root privileges.{Colors.RESET}")
        return

    def signal_handler(sig, frame):
        print(f"\n\n{Colors.YELLOW}Interrupted by user...{Colors.RESET}")
        display_statistics(sent, received, rtts, dest_addr, no_color)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    packet_id = 0x1234
    sent = 0
    received = 0
    rtts = []
    seq = 0

    while True:
        if not continuous and seq >= count:
            break

        seq += 1
        packet = build_icmp_packet(packet_id, seq)
        start_time = time.time()
        sent += 1

        try:
            sock.sendto(packet, (dest_addr, 80))

            readable = select.select([sock], [], [], timeout)
            if readable[0]:
                recv_packet, addr = sock.recvfrom(1024)
                rtt = (time.time() - start_time) * 1000

                icmp_header = recv_packet[20:28]
                reply_type, _, _, recv_id, recv_seq = struct.unpack(
                    '!BBHHH', icmp_header
                )

                if reply_type == 0 and recv_id == packet_id:
                    received += 1
                    rtts.append(rtt)

                    if not no_color:
                        color = get_color(rtt)
                    else:
                        color = ""

                    print(f"{color}{seq:3d}: Reply from {dest_addr}: "
                          f"bytes=32 time={rtt:.2f}ms TTL=64"
                          f"{Colors.RESET if not no_color else ''}")
                else:
                    print(f"{Colors.RED if not no_color else ''}"
                          f"{seq:3d}: Unexpected reply received "
                          f"(type={reply_type})"
                          f"{Colors.RESET if not no_color else ''}")
            else:
                print(f"{Colors.RED if not no_color else ''}"
                      f"{seq:3d}: Request timed out"
                      f"{Colors.RESET if not no_color else ''}")

        except Exception as e:
            print(f"{Colors.RED if not no_color else ''}"
                  f"{seq:3d}: Error during ping: {e}"
                  f"{Colors.RESET if not no_color else ''}")

        if continuous or (seq < count):
            time.sleep(1)

    display_statistics(sent, received, rtts, dest_addr, no_color)
    sock.close()


def display_statistics(sent, received, rtts, host, no_color=False):
    """Displays ping statistics with color coding."""
    if sent == 0:
        print(f"\n{Colors.RED}No packets sent.{Colors.RESET}")
        return

    separator = f"{'─' * 55}"

    print(f"\n{Colors.BOLD}{separator}")
    print(f"Ping statistics for {host}:")
    print(f"{separator}{Colors.RESET}")

    packet_loss = ((sent - received) / sent) * 100

    if not no_color:
        loss_color = get_loss_color(packet_loss)
    else:
        loss_color = ""

    print(f"    Packets: sent = {Colors.BOLD}{sent}{Colors.RESET}, "
          f"received = {Colors.GREEN if not no_color else ''}{received}"
          f"{Colors.RESET if not no_color else ''}, "
          f"lost = {loss_color}{sent - received}{Colors.RESET if not no_color else ''} "
          f"({loss_color}{packet_loss:.1f}% loss{Colors.RESET if not no_color else ''})")

    if rtts:
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        avg_rtt = sum(rtts) / len(rtts)

        variance = sum((x - avg_rtt) ** 2 for x in rtts) / len(rtts)
        std_dev = variance ** 0.5

        if not no_color:
            min_color = get_color(min_rtt)
            max_color = get_color(max_rtt)
            avg_color = get_color(avg_rtt)
        else:
            min_color = max_color = avg_color = ""

        print(f"    Round-trip times (ms):")
        print(f"        Minimum       = {min_color}{min_rtt:.2f}ms"
              f"{Colors.RESET if not no_color else ''}")
        print(f"        Maximum       = {max_color}{max_rtt:.2f}ms"
              f"{Colors.RESET if not no_color else ''}")
        print(f"        Average       = {avg_color}{avg_rtt:.2f}ms"
              f"{Colors.RESET if not no_color else ''}")
        print(f"        Std deviation = {std_dev:.2f}ms")
    else:
        print(f"    {Colors.RED}No successful replies received.{Colors.RESET}")

    print(f"{Colors.BOLD}{separator}{Colors.RESET}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ping utility with color coding and raw ICMP sockets.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Color legend:
  ┌─────────────────────────────────────┐
  │ Green   (RTT < 50ms)   - Excellent  │
  │ Yellow  (RTT < 150ms)  - Acceptable │
  │ Red     (RTT ≥ 150ms)  - Poor       │
  └─────────────────────────────────────┘

Examples:
  sudo python3 %(prog)s 8.8.8.8
  sudo python3 %(prog)s google.com -c 10
  sudo python3 %(prog)s 192.168.1.1 --continuous
  sudo python3 %(prog)s example.org -t 5 --no-color
"""
    )
    parser.add_argument(
        'target',
        metavar='<IP-address>',
        help='Target IP address or hostname to ping'
    )
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=4,
        help='Number of echo requests to send (default: 4)'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=2.0,
        help='Timeout in seconds per packet (default: 2.0s)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Ping continuously until Ctrl+C is pressed'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable color coding'
    )

    args = parser.parse_args()

    if args.continuous and args.count != 4:
        print(f"{Colors.YELLOW}Warning: --count is ignored when using --continuous{Colors.RESET}")

    ping(
        args.target,
        timeout=args.timeout,
        count=args.count,
        continuous=args.continuous,
        no_color=args.no_color
    )
